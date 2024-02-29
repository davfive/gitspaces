package helper

import (
	"fmt"
	"runtime/debug"
)

func GetStringAtIndex(array []string, index int, fallback string) string {
	if index < len(array) {
		return array[index]
	}
	return fallback
}

func FindIndexOf(array []string, target string) int {
	for index, value := range array {
		if value == target {
			return index
		}
	}
	return -1
}

func GetBuildVersion() string {
	settings, ok := getBuildSettings([]string{"vcs.revision", "vcs.modified"})
	if !ok {
		return ""
	}

	modified := settings["vcs.modified"]
	if modified == "false" {
		return fmt.Sprintf("%s", settings["vcs.revision"])
	} else {
		return fmt.Sprintf("%s-dirty", settings["vcs.revision"])
	}
}

func getBuildSettings(settings []string) (map[string]string, bool) {
	buildInfo, ok := debug.ReadBuildInfo()
	if !ok {
		return nil, false
	}

	infoMap := map[string]string{}
	for _, setting := range buildInfo.Settings {
		infoMap[setting.Key] = setting.Value
	}
	return infoMap, true
}
