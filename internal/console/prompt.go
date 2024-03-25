package console

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"strings"

	"github.com/charmbracelet/huh"
	"github.com/davfive/gitspaces/v2/internal/utils"
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
}

func NewInput() *Input {
	return &Input{
		value:    new(string),
		validate: func(s string) error { return nil },
	}
}

func NewOption[T comparable](title string, value T) Option[T] {
	return Option[T]{Title: title, Value: value}
}

func NewSelect[T comparable]() *Select[T] {
	return &Select[T]{
		options: []Option[T]{},
		value:   new(T),
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
	if validate == nil {
		i.validate = func(s string) error { return nil }
	} else {
		i.validate = validate
	}
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

func (i *Input) Run() error {
	if UsePrettyPrompts {
		return huh.NewInput().
			Title(i.title).
			Prompt(i.prompt).
			Value(i.value).
			Validate(i.validate).
			Run()
	}

	// For Dumb Terminals that Go prompt libraries don't support
	// e.g., Windows Powershell, Git Bash, Cygwin
	r := bufio.NewReader(os.Stdin)

	if i.title != "" {
		fmt.Fprintln(os.Stderr, i.title)
	}
	input := ""
	for i.validate(input) != nil {
		fmt.Fprintf(os.Stderr, "%s ", i.prompt)
		input, _ = r.ReadString('\n')
		input = strings.TrimSpace(input)
	}
	*i.value = input
	return nil
}

func (s *Select[T]) Run() error {
	if UsePrettyPrompts {
		return huh.NewSelect[T]().
			Title(s.title).
			Options(huh.NewOptions(s.rawOptions...)...).
			Value(s.value).
			Run()
	}

	// For Dumb Terminals that Go prompt libraries don't support
	// e.g., Windows Powershell, Git Bash, Cygwin

	fmt.Fprintf(os.Stderr, "\n")
	if s.title != "" {
		fmt.Fprintln(os.Stderr, s.title)
	}
	for i, option := range s.options {
		fmt.Fprintf(os.Stderr, "%2d: %s\n", i+1, option.Title)
	}

	input := NewInput().
		Prompt(utils.Get(s.prompt, "#?")).
		Validate(func(input string) error {
			if i, err := strconv.Atoi(input); err != nil || i < 1 || i > len(s.options) {
				return errors.New("invalid choice")
			}
			return nil
		})
	err := input.Run()
	if err == nil {
		optidx, _ := strconv.Atoi(*input.value)
		*s.value = s.options[optidx-1].Value
	}
	return err
}
