package cmd

import (
	"fmt"
	"slices"
)

func UseWhere(use string, whereArgs []WhereArg) string {
	// cmd.Command.Use expects a string (why I can't use UseWhereStruct as Stringer)
	return useWhereStruct{use, whereArgs}.String()
}

type WhereArg struct {
	Arg   string
	Short string
}

func (w WhereArg) Len() int {
	return len(w.Arg)
}

type useWhereStruct struct {
	Use       string
	WhereArgs []WhereArg
}

func (uw useWhereStruct) String() string {
	use := uw.Use
	if len(uw.WhereArgs) > 0 {
		// Leave order of whereArgs as specified by the caller
		use = use + "\n\nWhere:"
		maxArgWidth := uw.whereArgMaxLen()
		for _, where := range uw.WhereArgs {
			use = use + fmt.Sprintf("\n  %-*s\t%s", maxArgWidth, where.Arg, where.Short)
		}
	}
	return use
}

func (uw useWhereStruct) whereArgMaxLen() int {
	widestWhereArg := slices.MaxFunc(uw.WhereArgs[:], func(a, b WhereArg) int {
		return a.Len() - b.Len()
	})
	return widestWhereArg.Len()
}
