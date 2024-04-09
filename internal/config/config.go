package config

var Debug bool = false

var User *userStruct

const (
	GsDotDir      = ".gitspaces"
	GsProjectFile = "__GITSPACES_PROJECT__"
	GsSleeperDir  = ".zzz"
	GsVsCodeWsDir = ".code-workspace"
)

func Init(wrapId int) (err error) {
	User, err = initUser(wrapId)
	return err
}

func ProjectPaths() []string {
	return User.projectPaths
}
