package console

import (
	"fmt"
	"runtime"

	"github.com/charmbracelet/huh"
)

// Windows (powershell, cygwin, git bash) aren't propertly
// supported with pretty prompts (promptui or huh)
// So we'll use raw reads for these "dumb" terminals
var UsePrettyPrompts = runtime.GOOS != "windows"

type Input struct {
	title    string
	prompt   string
	value    *string
	validate func(string) error
}

type Option[T comparable] struct {
	Title string
	Value T
}

type Select[T comparable] struct {
	title      string
	prompt     string
	rawOptions []T
	options    []Option[T]
	value      *T
	validate   func(T) error
}

func NewInput() *Input {
	return &Input{
		value:    new(string),
		validate: func(string) error { return nil },
	}
}

func NewOption[T comparable](title string, value T) Option[T] {
	return Option[T]{Title: title, Value: value}
}

func NewSelect[T comparable]() *Select[T] {
	return &Select[T]{
		options:  []Option[T]{},
		value:    new(T),
		validate: func(T) error { return nil },
	}
}

func (i *Input) Prompt(prompt string) *Input {
	i.prompt = prompt
	return i
}

func (i *Input) Title(title string) *Input {
	i.title = title
	return i
}

func (i *Input) Validate(validate func(string) error) *Input {
	i.validate = validate
	return i
}

func (i *Input) Value(value *string) *Input {
	i.value = value
	return i
}

func (s *Select[T]) Title(title string) *Select[T] {
	s.title = title
	return s
}

func (s *Select[T]) Prompt(prompt string) *Select[T] {
	s.prompt = prompt
	return s
}

func (s *Select[T]) Options(optionsArray []T) *Select[T] {
	s.rawOptions = optionsArray
	for _, value := range optionsArray {
		s.options = append(s.options, NewOption(fmt.Sprintf("%v", value), value))
	}
	return s
}

func (s *Select[T]) Value(value *T) *Select[T] {
	s.value = value
	return s
}

func (s *Select[T]) Validate(validate func(T) error) *Select[T] {
	s.validate = validate
	return s
}

func (i *Input) Run() error {
	if UsePrettyPrompts {
		return huh.NewInput().
			Title(i.title).
			Prompt(i.prompt).
			Value(i.value).
			Validate(i.validate).
			Run()
	}
	return nil
}

func (s *Select[T]) Run() error {
	if UsePrettyPrompts {
		return huh.NewSelect[T]().
			Title(s.title).
			Options(huh.NewOptions(s.rawOptions...)...).
			Value(s.value).
			Validate(s.validate).
			Run()
	}
	return nil
}
