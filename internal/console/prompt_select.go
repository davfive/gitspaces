package console

import (
	"errors"
	"fmt"
	"os"
	"strconv"

	"github.com/charmbracelet/huh"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

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

func NewOption[T comparable](title string, value T) Option[T] {
	return Option[T]{Title: title, Value: value}
}

func NewSelect[T comparable]() *Select[T] {
	return &Select[T]{
		options: []Option[T]{},
		value:   new(T),
	}
}

func (s *Select[T]) Title(title string, a ...any) *Select[T] {
	s.title = fmt.Sprintf(title, a...)
	return s
}

func (s *Select[T]) Prompt(prompt string, a ...any) *Select[T] {
	s.prompt = fmt.Sprintf(prompt, a...)
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

func (s *Select[T]) Run() error {
	if usePrettyPrompts {
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
