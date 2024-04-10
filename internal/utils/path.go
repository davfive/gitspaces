package utils

// filepath uses the OS-specific path separator, so we need to convert it to a forward slash (which also works on Windows).

import (
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
)

func Abs(path string) (abs string, err error) {
	if abs, err = filepath.Abs(path); err == nil {
		abs = ToSlash(abs)
	}
	return abs, err
}

func Basename(path string, ext string) string {
	if ext != "" && strings.HasSuffix(path, ext) {
		return strings.TrimSuffix(filepath.Base(path), ext)
	}
	return filepath.Base(path)
}

func CreateEmptyFile(path string) (err error) {
	if err = os.MkdirAll(Dir(path), os.ModePerm); err != nil {
		return err
	}

	var file *os.File
	if file, err = os.Create(path); err != nil {
		return err
	}

	defer file.Close()
	return nil
}

func CreateEmptyFileIfNotExists(path string) (err error) {
	if PathExists(path) {
		return nil
	}

	return CreateEmptyFile(path)
}

func CygwinizePath(path string) string {
	driveRe := regexp.MustCompile("^(?P<drive>[A-z]+):")
	path = driveRe.ReplaceAllString(path, "/${drive}")
	path = strings.ReplaceAll(path, "\\", "/")
	return path
}

func Dir(path string) string {
	return ToSlash(filepath.Dir(path))
}

func EvalSymlinks(path string) (string, error) {
	if evalpath, err := filepath.EvalSymlinks(path); err == nil {
		return ToSlash(evalpath), nil
	} else {
		return "", err
	}
}

func Filename(path string) string {
	return Basename(path, "")
}

func FilterDirectories(paths []string) []string {
	var dirs []string
	for _, path := range paths {
		if PathIsDir(path) {
			dirs = append(dirs, path)
		}
	}
	return dirs
}

// GetCygpathHomeDir returns the user's ~/ dir from the cygpath command.
// If cygpath doesn't exist (either not on Windows or Cygwin is not installed)
// then the normal $USERPROFILE or /Users/<username> is returned. This
// method is only used to determine the location of the user's rc file for
// setup, in all other cases the user's home dir is the normal one.
// Note: on windows in powershell, this resolves to the cygwin home dir (unexpectedly)
func GetCygwinAwareHomeDir() string {
	if runtime.GOOS != "windows" || GetTerminalType() == "pwsh" {
		return GetUserHomeDir()
	}

	cmd := exec.Command("cygpath", "-m", "~")
	out, err := cmd.Output()
	if err != nil {
		return GetUserHomeDir()
	}
	return ToSlash(strings.TrimSpace(string(out))) // Already Cygwinized
}

func GetUserHomeDir() string {
	userHomeDir, err := os.UserHomeDir()
	PanicIfError(err)
	return ToSlash(userHomeDir)
}

func GetShellHomeDir() string {
	return GetCygwinAwareHomeDir()
}

func Getwd() string {
	dir, err := os.Getwd()
	PanicIfError(err)
	return ToSlash(dir)
}

func Join(paths ...string) string {
	return ToSlash(filepath.Join(paths...))
}

func PathIsDir(filename string) bool {
	info, err := os.Stat(filename)
	return !errors.Is(err, os.ErrNotExist) && info.IsDir()
}

func PathExists(filename string) bool {
	_, err := os.Stat(filename)
	return !errors.Is(err, os.ErrNotExist)
}

func PathIsFile(filename string) bool {
	info, err := os.Stat(filename)
	return os.IsExist(err) && !info.IsDir()
}

func Rel(basepath string, targpath string) (string, error) {
	if relPath, err := filepath.Rel(basepath, targpath); err == nil {
		return ToSlash(relPath), nil
	} else {
		return targpath, err
	}
}

func ToSlash(path string) string {
	// Note that filepath.ToSlash() is a no-op on *nix.
	// If I am concerned about people using windows path on *nix,
	// I should use strings.ReplaceAll(path, "\\", "/") instead.
	return filepath.ToSlash(path)
}
