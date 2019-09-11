echo "Running gitspaces.config ..."

# ini file parser
function gs_config() {
	local spacesdir=${spacesdir:=$(getspacesdir)}
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1
	local inifile="$spacesdir/../$GITSPACES_CONFIG"

  case "$1" in
    list)
  	  local sectionre=$2
      for section in $(cat $inifile | grep -E "\[$sectionre" | sed -e "s#\[##g" | sed -e "s#\]##g"); do
        echo "$section"
      done
      return 0
      ;;
    get)
  	  local sectionre=$2
      local key=$3

      # https://stackoverflow.com/questions/49399984/parsing-ini-file-in-bash
      # This awk line turns ini sectins => [section-name]key=value
      local lines=$(awk '/\[/{prefix=$0; next} $1{print prefix $0}' $inifile)
      local rckey=1 # not found
      for line in $lines; do
        echo "$line" | grep -q -E "^\[$sectionre"
        if [ $? -eq 0 ]; then
          local keyval=$(echo $line | sed -e "s/^\[$sectionre.*\]//")
          if [[ -z "$key" ]]; then
            echo $keyval
          else			
            if [[ "$keyval" = $key=* ]]; then
              echo $(echo $keyval | sed -e "s/^$key=//")
              rckey=0
            fi
          fi
        fi
      done
      [[ ! -x "$key" ]] && return $rckey
      return 0
      ;;
   *)
		  echo "usage: gs_config list [<section-regex>]"
      echo "usage: gs_config get  <section-reqex> [key]"
		  return 1
      ;;
	esac
}

function gs_config_brset_select() {
	local inifile="$spacesdir/$GITSPACES_CONFIG"
	local spacesdir=${spacesdir:=$(getspacesdir)}
	[ ! -d "$(gs_checkspacesdir "$spacesdir")" ] && return 1

  local brsets=$(gs_config list BranchSet | sed 's/BranchSet://')
  local brset
  # Choose a branch set
  while [ "x$brset" == "x" ]; do
    PS3="Select a BranchSet: "
    select brset in $brsets; do
      break
    done
  done
  if [[ -z "$brset" ]]; then
    return 1
  else
    echo $brset
    return 0
  fi
}


