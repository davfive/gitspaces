package utils

import (
	"cmp"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"slices"
	"strings"
	"text/template"

	"golang.org/x/exp/maps"
)

func CygwinizePath(path string) string {
	driveRe := regexp.MustCompile("^(?P<drive>[A-z]+):")
	path = driveRe.ReplaceAllString(path, "/${drive}")
	path = strings.Replace(path, "\\", "/", -1)
	return path
}

func GetIndex[S ~[]E, E any](s S, index int, fallback E) E {
	if index < len(s) {
		return s[index]
	}
	return fallback
}

func Get[E comparable](v E, fallbacks ...E) E {
	var zero E
	if v != zero {
		return v
	} else {
		for _, f := range fallbacks {
			if f != zero {
				return f
			}
		}
		return zero
	}
}

func MakeDirnameAvailableValidator(parentDir string) func(string) error {
	return func(dirname string) error {
		if strings.HasPrefix(dirname, ".") || PathExists(filepath.Join(parentDir, dirname)) {
			return errors.New("invalid")
		}
		return nil
	}
}

func OpenFileInDefaultApp(path string) error {
	switch runtime.GOOS {
	case "windows":
		return exec.Command("cmd", "/c", path).Start()
	case "darwin":
		return exec.Command("open", path).Start()
	default:
		return fmt.Errorf("unsupported OS: %s", runtime.GOOS)
	}
}

func SortKeys[M ~map[K]V, K cmp.Ordered, V any](m M) []K {
	keys := maps.Keys(m)
	slices.Sort(keys)
	return keys
}

func Executable() (exe string) {
	var err error

	if exe, err = os.Executable(); err == nil {
		if exe, err = filepath.EvalSymlinks(exe); err == nil {
			return exe
		}
	}
	return os.Args[0]
}

func SafeWriteTemplateToFile(t *template.Template, path string, vars map[string]interface{}) (err error) {
	if PathExists(path) {
		return errors.New("template path already exists: " + path)
	}

	return WriteTemplateToFile(t, path, vars)
}

func WriteTemplateToString(tmpl *template.Template, vars map[string]interface{}) (string, error) {
	var s strings.Builder
	err := tmpl.Execute(&s, vars)
	return s.String(), err
}

func WriteTemplateToFile(tmpl *template.Template, path string, vars map[string]interface{}) (err error) {
	if err = os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}

	var f *os.File
	if f, err = os.Create(path); err != nil {
		return err
	}

	err = tmpl.Execute(f, vars)
	f.Close()
	return err
}
