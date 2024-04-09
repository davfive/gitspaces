package console

import (
	"errors"
	"fmt"
	"os"
	"slices"
	"strings"

	"github.com/charmbracelet/huh"
	"github.com/davfive/gitspaces/v2/internal/utils"
)

type Confirm struct {
	title       string
	prompt      string
	affirmative string
	negative    string
	value       *bool
}

func NewConfirm() *Confirm {
	return &Confirm{
		affirmative: "Yes",
		negative:    "No",
		value:       new(bool),
	}
}

func (c *Confirm) Affirmative(affirmative string) *Confirm {
	c.affirmative = affirmative
	return c
}

func (c *Confirm) Negative(negative string) *Confirm {
	c.negative = negative
	return c
}

func (c *Confirm) Title(title string) *Confirm {
	c.title = title
	return c
}

func (c *Confirm) Prompt(title string, a ...any) *Confirm {
	c.title = fmt.Sprintf(title, a...)
	return c
}

func (c *Confirm) Value(value *bool) *Confirm {
	c.value = value
	return c
}

func (c *Confirm) Run() bool {
	prompt := utils.Get(c.prompt, c.title, "Confirm?")
	if usePrettyPrompts {
		err := huh.NewConfirm().
			Title(prompt).
			Value(c.value).
			Run()
		if err != nil {
			*c.value = false
		}
		return *c.value
	}

	// For Dumb Terminals that Go prompt libraries don't support
	// e.g., Windows Powershell, Git Bash, Cygwin

	fmt.Fprintf(os.Stderr, "\n")
	if c.title != prompt {
		fmt.Fprintln(os.Stderr, c.title)
	}

	input := NewInput().
		Prompt(prompt).
		Validate(func(input string) error {
			foundMatch := false
			if input != "" {
				slices.ContainsFunc([]string{c.affirmative, c.negative}, func(v string) bool {
					return strings.EqualFold(v, input) || strings.EqualFold(v[0:1], input[0:1])
				})
			}
			if !foundMatch {
				return errors.New("invalid choice")
			}
			return nil
		})
	err := input.Run()
	if err != nil {
		if *input.value == c.affirmative {
			*c.value = true
		} else {
			*c.value = false
		}
	}
	return *c.value
}
