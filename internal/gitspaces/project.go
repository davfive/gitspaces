package gitspaces

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"slices"

	"github.com/davfive/gitspaces/v2/internal/config"
	"github.com/davfive/gitspaces/v2/internal/console"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

type ProjectStruct struct {
	Path      string
	Name      string
	codeWsDir string
	dotfile   string
	zzzdir    string
}

// Create creates the Project directory, dotfile, sleeping clones, and the default
// clone in the spaces' working directory named after the repo's default branch.
// It returns a pointer to the Project object or an error
func CreateProject(dir string, url string, numSpaces int) (project *ProjectStruct, err error) {
	var projectPath string
	if projectPath, err = getNewProjectPath(dir, url); err != nil {
		return nil, err
	}

	project = NewProject(projectPath)
	if err = project.init(); err != nil {
		return nil, err
	}

	firstSpace, err := CreateSpaceFromUrl(project, url, project.getEmptySleeperPath())
	if err != nil {
		return nil, err
	}

	for i := 1; i < numSpaces; i++ {
		if _, err := firstSpace.Duplicate(); err != nil {
			return nil, err
		}
	}

	return project, nil
}

func GetProjectFromPath(path string) (*ProjectStruct, error) {
	switch {
	case path == "":
	case !utils.PathExists(path):
		return nil, errors.New("path not found")
	case utils.PathIsFile(path):
		path = utils.Dir(path)
	}

	var prevPath string
	for currPath := path; currPath != prevPath; currPath = utils.Dir(currPath) {
		if utils.PathExists(utils.Join(currPath, config.GsProjectFile)) {
			return NewProject(currPath), nil
		}
		prevPath = currPath
	}

	return nil, errors.New("no project found from " + path)
}

func GetProject() (*ProjectStruct, error) {
	return GetProjectFromPath(utils.Getwd())
}

func NewProject(path string) (project *ProjectStruct) {
	path = utils.ToSlash(path)
	project = &ProjectStruct{
		Path:      path,
		Name:      utils.Filename(path),
		codeWsDir: utils.Join(path, config.GsVsCodeWsDir),
		dotfile:   utils.Join(path, config.GsProjectFile),
		zzzdir:    utils.Join(path, config.GsSleeperDir),
	}
	return project
}

func ChooseProject() (project *ProjectStruct, err error) {
	projectPaths := []string{}
	for _, path := range config.ProjectPaths() {
		paths, _ := filepath.Glob(utils.Join(path, "*", config.GsProjectFile))
		for i := range paths {
			paths[i] = utils.Dir(paths[i])
		}
		projectPaths = append(projectPaths, paths...)
	}
	slices.Sort(projectPaths)

	var projectPath string
	err = console.NewSelect[string]().
		Title("Choose a project").
		Options(projectPaths).
		Value(&projectPath).
		Run()
	if err != nil {
		return nil, err
	}

	return GetProjectFromPath(projectPath)
}

func SwitchSpace() (space *SpaceStruct, err error) {
	// Just switch spaces if we're already in a project
	var project *ProjectStruct
	if project, _ = GetProject(); project == nil {
		if project, err = ChooseProject(); err != nil {
			return nil, err
		}
	}

	space, err = project.ChooseSpace()
	if err != nil {
		return nil, err
	}

	return space, nil
}

func getNewProjectPath(dir string, url string) (projectPath string, err error) {
	projectsDir := utils.Getwd()

	// Let user chose which ProjectPaths to put the new project in
	err = console.NewSelect[string]().
		Title("Create project in:").
		Options(config.ProjectPaths()).
		Value(&projectsDir).
		Run()
	if err != nil {
		return "", err
	}

	// Get this project directory name
	if dir == "" {
		dir = utils.Basename(url, ".git")
	}

	err = console.NewInput().
		Prompt("Project Directory: ").
		Validate(console.MakeDirnameAvailableValidator(projectsDir)).
		Value(&dir).
		Run()

	return utils.Join(projectsDir, dir), nil
}

func switchProject() (space *SpaceStruct, err error) {
	// Force full switching of projects
	var project *ProjectStruct
	if project, err = ChooseProject(); err != nil {
		return nil, err
	}

	space, err = project.ChooseSpace()
	if err != nil {
		return nil, err
	}

	return space, nil
}

func (project *ProjectStruct) ChooseSpace() (space *SpaceStruct, err error) {
	spaceNames := []string{".."}
	workerSpaces := project.getWorkerSpaces()
	for _, space := range workerSpaces {
		spaceNames = append(spaceNames, space.Name)
	}
	numSleepers := len(project.getSleeperSpacePaths())
	if numSleepers > 0 {
		spaceNames = append(spaceNames, fmt.Sprintf("[Wakeup] (%d)", numSleepers))
	}

	var spaceName string
	err = console.NewSelect[string]().
		Title("Choose a Space").
		Options(spaceNames).
		Value(&spaceName).
		Run()
	if err != nil {
		return nil, err
	}

	idx := slices.Index(spaceNames, spaceName)
	if idx == 0 {
		return switchProject()
	} else if numSleepers > 0 && idx == len(spaceNames)-1 {
		return project.WakeupSpace()
	} else {
		return workerSpaces[idx-1], nil
	}
}

func (project *ProjectStruct) WakeupSpace() (space *SpaceStruct, err error) {
	if space, err = project.getLastSleeperSpace(); err != nil {
		return nil, err
	}

	if err = space.Wakeup(); err != nil {
		return nil, err
	}

	return space, nil
}

func (project *ProjectStruct) getSleeperSpacePaths() []string {
	paths, _ := filepath.Glob(utils.Join(project.zzzdir, "zzz-*"))
	return utils.FilterDirectories(paths)
}

func (project *ProjectStruct) getWorkerSpacePaths() []string {
	paths, _ := filepath.Glob(utils.Join(project.Path, "[^.]*"))
	return utils.FilterDirectories(paths)
}

func (project *ProjectStruct) getWorkerSpaces() (spaces []*SpaceStruct) {
	for _, path := range project.getWorkerSpacePaths() {
		spaces = append(spaces, NewSpace(project, path))
	}
	return spaces
}

func (project *ProjectStruct) getLastSleeperSpace() (space *SpaceStruct, err error) {
	sleepers := project.getSleeperSpacePaths()
	if len(sleepers) == 0 {
		return nil, errors.New("no sleeper found")
	}

	lastSpacePath := utils.Join(project.zzzdir, fmt.Sprintf("zzz-%d", len(sleepers)-1))
	if !utils.PathExists(lastSpacePath) {
		return nil, errors.New("no sleeper found at " + lastSpacePath)
	}
	return NewSpace(project, lastSpacePath), nil
}

func (project *ProjectStruct) getEmptySleeperPath() string {
	sleepers := project.getSleeperSpacePaths()
	return utils.Join(project.zzzdir, fmt.Sprintf("zzz-%d", len(sleepers)))
}

func (project *ProjectStruct) init() error {
	if utils.PathExists(project.Path) {
		return errors.New("GitSpaces Project path already exists")
	}

	// Create the Project directories
	for _, path := range []string{project.Path, project.zzzdir, project.codeWsDir} {
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			return err
		}
	}

	// Create blank Project config
	err := utils.CreateEmptyFile(utils.Join(project.Path, config.GsProjectFile))
	if err != nil {
		return err
	}

	return nil
}

func (project *ProjectStruct) isWellFormed() bool {
	for _, path := range []string{project.Path, project.zzzdir, project.codeWsDir} {
		if !utils.PathIsDir(path) {
			return false
		}
	}

	return true
}
