package console

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/huh"
)

type Input struct {
	title    string
	prompt   string
	value    *string
	validate func(string) error
}

func NewInput() *Input {
	return &Input{
		value:    new(string),
		validate: func(s string) error { return nil },
	}
}

func (i *Input) Prompt(prompt string, a ...any) *Input {
	i.prompt = fmt.Sprintf(prompt, a...)
	return i
}

func (i *Input) Title(title string, a ...any) *Input {
	i.title = fmt.Sprintf(title, a...)
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

func (i *Input) Run() error {
	if usePrettyPrompts {
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
	for {
		fmt.Fprintf(os.Stderr, "%s ", i.prompt)
		input, _ = r.ReadString('\n')
		input = strings.TrimSpace(input)
		if err := i.validate(input); err == nil {
			break
		}
	}
	*i.value = input
	return nil
}
