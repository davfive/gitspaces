package utils

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

func CreateEmptyFile(path string) (err error) {
	if err = os.MkdirAll(filepath.Dir(path), os.ModePerm); err != nil {
		return err
	}

	var file *os.File
	if file, err = os.Create(path); err != nil {
		return err
	}

	defer file.Close()
	return nil
}

func CreateFile(path string) (err error) {
	if err = os.MkdirAll(filepath.Dir(path), os.ModePerm); err != nil {
		return err
	}

	var file *os.File
	if file, err = os.Create(path); err != nil {
		return err
	}

	defer file.Close()
	return nil
}

func GetUserHomeDir() string {
	userHomeDir, err := os.UserHomeDir()
	PanicIfError(err)
	return userHomeDir
}

func PathExists(filename string) bool {
	_, err := os.Stat(filename)
	return !errors.Is(err, os.ErrNotExist)
}

func PathIsFile(filename string) bool {
	info, err := os.Stat(filename)
	return os.IsExist(err) && !info.IsDir()
}

func PathIsDir(filename string) bool {
	info, err := os.Stat(filename)
	return !errors.Is(err, os.ErrNotExist) && info.IsDir()
}

func Getwd() string {
	dir, err := os.Getwd()
	PanicIfError(err)
	return dir
}

func FileBase(path string, ext string) string {
	if ext == "" {
		return filepath.Base(path)
	}
	return strings.TrimSuffix(filepath.Base(path), filepath.Ext(ext))
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
