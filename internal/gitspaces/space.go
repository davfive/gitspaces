package gitspaces

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"

	cp "github.com/otiai10/copy"
)

// Gitspace is a struct that represents a git repository
type SpaceStruct struct {
	Name       string
	Path       string
	project    *ProjectStruct
	codeWsFile string
}

func CreateSpaceFromUrl(project *ProjectStruct, url string, path string) (space *SpaceStruct, err error) {
	// go-git doesn't have a robust ssh-cloning implementation (gits tripped up easily by ssh config, )
	cmd := exec.Command("git", "clone", url, path)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err = cmd.Run(); err != nil {
		return nil, err
	}

	space = NewSpace(project, path)

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
	return GetSpaceFromPath(utils.Getwd())
}

// NewSpace creates a new Space struct
func NewSpace(project *ProjectStruct, path string) *SpaceStruct {
	space := &SpaceStruct{
		Path:    utils.ToSlash(path),
		project: project,
	}
	space.updateName()
	space.createCodeWorkspaceFile()
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
	space.Name = utils.Filename(space.Path)
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

	// Ensure it has the correct name (and vscode on windows requires forward slashes in the path)
	space.codeWsFile = utils.Join(
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
}`, strings.Replace(space.Path, "\\", "/", -1)))

	return err
}

func (space *SpaceStruct) deleteCodeWorkspaceFile() (err error) {
	if utils.PathExists(space.codeWsFile) {
		if err = os.Remove(space.codeWsFile); err != nil {
			fmt.Fprintln(os.Stderr, "Failed to remove "+space.codeWsFile)
			return err
		}
	}
	return nil
}

func (space *SpaceStruct) move(moveVerb string, arguments ...string) error {
	var newName string // wishing for default args and/or a ternary operator :/
	if len(arguments) > 0 {
		newName = arguments[0]
	}
	err := console.NewInput().
		Prompt(fmt.Sprintf("%s space as: ", moveVerb)).
		Validate(console.MakeDirnameAvailableValidator(space.project.Path)).
		Value(&newName).
		Run()
	if err != nil {
		return err
	}

	newPath := utils.Join(space.project.Path, newName)
	space.deleteCodeWorkspaceFile()
	os.Chdir(space.project.Path)
	if err = os.Rename(space.Path, newPath); err != nil {
		os.Chdir(space.Path)
		return err
	}

	space.Path = newPath
	space.Name = newName
	os.Chdir(space.Path)

	if err = space.createCodeWorkspaceFile(); err != nil {
		fmt.Fprintln(os.Stderr, "Failed to create code workspace file")
	}

	return nil
}

func (space *SpaceStruct) updateName() {
	// It would just be utils.Filename(space.path) but we have to account for sleeper spaces (in .zzz dir)
	// The space.Name is used in the code-workspace file name so it can't have any separator characters
	space.Name, _ = utils.Rel(space.project.Path, space.Path)
	space.Name = strings.ReplaceAll(space.Name, "/", "~")
}
