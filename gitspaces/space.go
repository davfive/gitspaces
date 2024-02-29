package gitspaces

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/davfive/gitspaces/v2/console"
	"github.com/davfive/gitspaces/v2/helper"

	"github.com/go-git/go-git/v5"
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
	if _, err = git.PlainClone(path, false, &git.CloneOptions{
		URL:      url,
		Progress: os.Stdout,
	}); err != nil {
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
	return GetSpaceFromPath(helper.Getwd())
}

// NewSpace creates a new Space struct
func NewSpace(project *ProjectStruct, path string) *SpaceStruct {
	space := &SpaceStruct{
		Path:    path,
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

func (space *SpaceStruct) Rename() error {
	return space.move("Rename")
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

func (space *SpaceStruct) move(moveVerb string) error {
	name, err := console.GetUserInputWithValidation(
		fmt.Sprintf("%s space as", moveVerb),
		func(s string) error {
			checkpath := filepath.Join(space.project.Path, s)
			if strings.HasPrefix(s, ".") || helper.PathExists(checkpath) {
				return errors.New("invalid")
			}
			return nil
		},
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
