package gitspaces

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"strings"

	"github.com/davfive/gitspaces/v2/console"
	"github.com/davfive/gitspaces/v2/helper"

	cp "github.com/otiai10/copy"
)

type SpaceStat struct {
	space      *SpaceStruct
	wasStated  bool
	IsEmpty    bool
	numRepos   int
}

func NewSpaceStat(space *SpaceStruct) *SpaceStat {
	return &SpaceStat{
		space: space,
	}
}

func (stat *SpaceStat) stat() *SpaceStat {
	if stat.IsEmpty, err helper.DirectoryIsEmpty(space.Path) {
		
}


// Gitspace is a struct that represents a git repository
type SpaceStruct struct {
	Name       string
	Path       string
	Stat       *SpaceStat
	IsEmpty    bool
	IsMonoRepo bool
	project    *ProjectStruct
	codeWsFile string
}

func CreateSpace(project *ProjectStruct) *SpaceStruct {
	newSpace := NewSpace(project, project.getEmptySleeperPath())
	newSpace.init()
	return newSpace
}

func (space *SpaceStruct) spaceState() (int, error) {
	// Assumes space directory exists
	if isEmpty, err := helper.DirectoryIsEmpty(space.Path); err != nil {
		return -1, err
	}

	if isEmpty {
		return 0, nil
	}

	if helper.PathExists(filepath.Join(space.Path, ".git")) {
		return 1
	}

	

	if _, err := os.Stat(filepath.Join(space.Path, ".git")); !os.IsNotExist(err) {

	os.ReadDir(space.Path)

	return helper.CountDirs(space.Path)
}


func (space *SpaceStruct) AddRepoFromUrls(project *ProjectStruct, url string, path string) error {
	dir := strings.TrimSuffix(filepath.Base(url), ".git")

	if space.numRepos() > 0 {
		return errors.New("space already has a repo")
	}

	if _, err := os.Stat(filepath.Join(space.Path, dir)); err == nil {
		return errors.New("repo dir already exists in space")
	}

	space = NewSpace(project, path)
	urls = slices.Compact(urls)
	urlMap := make(map[string]string)
	for _, url := range urls {
		dir := strings.TrimSuffix(filepath.Base(url), ".git")
		if _, ok := urlMap[dir]; ok {
			urlMap[dir] = url
		} else {
			// TODO: We could ask the user if they want to use a different name for the duplicate
			return nil, errors.New("duplicate repo name in urls list: " + strings.Join(urls, ","))
		}
	}

	getRepoDir := func(dir string) string {
		if len(urls) == 1 {
			// single-repo spaces are cloned directly into the space directory
			// Makes the path shorter for simple projects
			return path
		}
		return filepath.Join(path, dir)
	}

	// go-git doesn't have a robust ssh-cloning implementation (gits tripped up easily by ssh config, )
	for dir, url := range urlMap {
		cmd := exec.Command("git", "clone", url, getRepoDir(dir))
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err = cmd.Run(); err != nil {
			return nil, err
		}
	}

	if err = space.createCodeWorkspaceFile(); err != nil {
		return nil, err
	}

	return space, nil
}

func GetSpaceFromPath(path string) (*SpaceStruct, error) {
	project, err := GetProjectFromPath(path) // Path is checked here
	if err != nil {
		return nil, err
	}

	for _, spacePath := range project.getWorkerSpacePaths() {
		if strings.HasPrefix(path, spacePath) {
			return NewSpace(project, spacePath), nil
		}
	}

	return nil, errors.New("space not found from " + path)
}

func GetSpace() (*SpaceStruct, error) {
	return GetSpaceFromPath(helper.Getwd())
}

// NewSpace creates a new Space struct
func NewSpace(project *ProjectStruct, path string) *SpaceStruct {
	space := &SpaceStruct{
		Path:    path,
		project: project,
	}
	space.Stat = NewSpaceStat(space)
	space.updateName()
	return space
}

func (space *SpaceStruct) Duplicate() (newSpace *SpaceStruct, err error) {
	copyToPath := space.project.getEmptySleeperPath()

	if err = cp.Copy(space.Path, copyToPath); err != nil {
		return nil, err
	}

	return NewSpace(space.project, copyToPath), nil
}

func (space *SpaceStruct) GetProject() *ProjectStruct {
	return space.project
}

func (space *SpaceStruct) OpenVSCode() error {
	codeExecPath, err := exec.LookPath("code")
	if err != nil {
		return err
	}
	return exec.Command(codeExecPath, space.codeWsFile).Start()
}

// Rename renames the space.
// It takes a variadic parameter of type string, which represents the optional new name for the space.
// If successful, it returns nil. Otherwise, it returns an error.
func (space *SpaceStruct) Rename(arguments ...string) error {
	return space.move("Rename", arguments...)
}

func (space *SpaceStruct) Sleep() (err error) {
	space.deleteCodeWorkspaceFile()

	newPath := space.project.getEmptySleeperPath()
	space.Name = filepath.Base(space.Path)
	if err = os.Rename(space.Path, newPath); err != nil {
		return err
	}
	space.deleteCodeWorkspaceFile()

	return nil
}

func (space *SpaceStruct) Wakeup() (err error) {
	return space.move("Wakeup")
}

func (space *SpaceStruct) createCodeWorkspaceFile() (err error) {
	var file *os.File

	// Ensure it has the correct name
	space.codeWsFile = filepath.Join(
		space.project.codeWsDir,
		fmt.Sprintf("%s~%s.code-workspace", space.project.Name, space.Name),
	)

	if file, err = os.Create(space.codeWsFile); err != nil {
		return err
	}
	defer file.Close()

	_, err = file.WriteString(fmt.Sprintf(`{
		"folders": [
			{
				"path": "%s"
			}
		],
		"settings": {}
	}`, space.Path))

	return err
}

func (space *SpaceStruct) deleteCodeWorkspaceFile() (err error) {
	if helper.PathExists(space.codeWsFile) {
		if err = os.Remove(space.codeWsFile); err != nil {
			fmt.Fprintln(os.Stderr, "Failed to remove "+space.codeWsFile)
			return err
		}
	}
	return nil
}

func (space *SpaceStruct) init() error {
	// Minimal setup for space, just create the space directory
	return os.MkdirAll(space.Path, os.ModePerm)
}

func (space *SpaceStruct) move(moveVerb string, arguments ...string) error {
	var newName string // pining for default args and/or a ternary operator :/
	if len(arguments) > 0 {
		newName = arguments[0]
	}
	name, err := console.GetUserInputWithValidation(
		fmt.Sprintf("%s space as", moveVerb),
		newName,
		console.MakeDirnameAvailableValidator(space.project.Path),
	)
	if err != nil {
		return err
	}

	newPath := filepath.Join(space.project.Path, name)
	space.deleteCodeWorkspaceFile()
	if err = os.Rename(space.Path, newPath); err != nil {
		return err
	}
	space.Path = newPath
	space.Name = name
	if err = space.createCodeWorkspaceFile(); err != nil {
		fmt.Fprintln(os.Stderr, "Failed to create code workspace file")
	}

	return nil
}

func (space *SpaceStruct) updateName() {
	// It would just be filepath.Base(space.path) but we have to account for sleeper spaces (in .zzz dir)
	// The space.Name is used in the code-workspace file name so it can't have any separator characters
	space.Name = strings.TrimPrefix(space.Path, space.project.Path+string(filepath.Separator))
	space.Name = strings.ReplaceAll(space.Name, string(filepath.Separator), "~")
}
