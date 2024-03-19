package helper

func GetStringAtIndex(array []string, index int, fallback string) string {
	if index < len(array) {
		return array[index]
	}
	return fallback
}

func FindIndexOf(array []string, target string) int {
	for index, value := range array {
		if value == target {
			return index
		}
	}
	return -1
}
