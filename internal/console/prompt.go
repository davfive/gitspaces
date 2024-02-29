package console

import (
	"fmt"

	"github.com/manifoldco/promptui"
)

func GetUserInput(label string) (string, error) {
	return GetUserInputWithValidation(label, nil)
}

func GetUserInputWithValidation(label string, validate func(string) error) (string, error) {
	prompt := promptui.Prompt{
		Label:       label,
		HideEntered: true,
		Validate:    validate,
	}

	return prompt.Run()
}

func GetUserChoice(context string, items []string) (int, string, error) {
	prompt := promptui.Select{
		Label:        fmt.Sprintf("Select %s", context),
		Items:        items,
		HideHelp:     true,
		HideSelected: true,
		Size:         10,
		Templates: &promptui.SelectTemplates{
			Label:    "{{ . }}",
			Active:   fmt.Sprintf(`{{ "%s" | cyan }} {{ . | cyan }}`, promptui.IconSelect),
			Inactive: "  {{ . | faint }}",
			Selected: fmt.Sprintf(
				`{{ "%s" | green }} {{ "%s: " . | faint }}`, promptui.IconGood, context,
			),
		},
	}

	return prompt.Run()
}
