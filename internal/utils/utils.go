package utils

import (
	"cmp"
	"errors"
	"os"
	"slices"
	"strings"
	"text/template"

	"github.com/mitchellh/go-ps"
	"github.com/skratchdot/open-golang/open"
	"golang.org/x/exp/maps"
)

func Executable() (exe string) {
	var err error

	if exe, err = os.Executable(); err == nil {
		if exe, err = EvalSymlinks(exe); err == nil {
			return exe
		}
	}
	return ToSlash(os.Args[0])
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

func GetIndex[S ~[]E, E any](s S, index int, fallback E) E {
	if index < len(s) {
		return s[index]
	}
	return fallback
}

func GetTerminalType() string {
	parentps, _ := ps.FindProcess(os.Getppid())
	if parentps == nil {
		return ""
	}

	parentProcessName := strings.ToLower(Basename(parentps.Executable(), ".exe"))
	switch parentProcessName {
	case "pwsh", "powershell":
		return "pwsh"
	case "bash", "zsh":
		return parentProcessName
	default:
		return ""
	}
}

func OpenFileInDefaultApp(path string) (err error) {
	if path, err = EvalSymlinks(path); err != nil {
		return err
	}

	if err = CreateEmptyFileIfNotExists(path); err != nil {
		return err
	}

	return open.Start(path)
}

func SafeWriteTemplateToFile(t *template.Template, path string, vars map[string]interface{}) (err error) {
	if PathExists(path) {
		return errors.New("template path already exists: " + path)
	}

	return WriteTemplateToFile(t, path, vars)
}

func SortKeys[M ~map[K]V, K cmp.Ordered, V any](m M) []K {
	keys := maps.Keys(m)
	slices.Sort(keys)
	return keys
}

func Ternary[T any](cond bool, a T, b T) T {
	if cond {
		return a
	}
	return b
}

func WriteTemplateToFile(tmpl *template.Template, path string, vars map[string]interface{}) (err error) {
	if err = os.MkdirAll(Dir(path), 0o755); err != nil {
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

func WriteTemplateToString(tmpl *template.Template, vars map[string]interface{}) (string, error) {
	var s strings.Builder
	err := tmpl.Execute(&s, vars)
	return s.String(), err
}
