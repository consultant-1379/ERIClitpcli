##############################################################################
# COPYRIGHT Ericsson AB 2013
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

function __has_type_children {
	while read json_line ; do
		if [[ ${json_line} == *_embedded* ]]; then
			return 0
		fi
	done << _EOSHOW
		$(litp show --path '/item-types/'${1} -j 2> /dev/null)
_EOSHOW
	return 1
}

function __litp_complete {
	local extglob_status=$(shopt -q extglob)
	local stem token last_token cursor_on_last_token previous_token
	local last_token_no_path
	local parent_path trailing_slash completion 
	shopt -s extglob

	local litp_cli=${COMP_LINE:0:${COMP_POINT}}
	# Do we have whitespace between the completion point and the right-most
	# token left of the completion point?
	[[ ${litp_cli} != ${litp_cli%% } ]]
	cursor_on_last_token=$?

	for token in ${litp_cli}; do
		previous_token=${last_token}
		last_token=${token}
	done

	if (( cursor_on_last_token )); then
		last_token_no_path=${last_token%%/*}
		if [[ ${last_token_no_path} == @(--path=|--source-path) ]]; then
			if [[ ${last_token} == ${last_token#*/} ]]; then
				stem='/'
			else
				stem=/${last_token#*/}
			fi
		else
			if [[ ${previous_token} == @(-*p|--path|-s|--source-path) ]]; then
				stem=${last_token}
			else
				return 1
			fi
		fi
	else
		if [[ ${last_token} == @(-*p|--path|-s|--source-path) ]]; then
			if [[ ${last_token} == */* ]]; then
				return 1
			else
				stem='/'
			fi
		else
			return 1
		fi
	fi

	local completion_stem=${stem%/*}
	local item_type

	[[ -z ${completion_stem} ]] && completion_stem='/'

	while read completion; do
		[[ ${completion} == ${completion_stem} ]] && continue
		[[ ${completion} == ${stem}* ]] || continue

		if [[ ${completion} == *:* ]]; then
			item_type=${completion#*:}
			completion=${completion%:*}

			__has_type_children ${item_type}
			if (( $? == 0 )); then
				completion="${completion}/"
			fi
		fi

		COMPREPLY+=( ${completion} )
	done << _EOSHOW
		$(litp show --path ${completion_stem:-/} -L 2> /dev/null)
_EOSHOW

	(( 0 == extglob_status )) && shopt -s extglob
	(( 1 == extglob_status )) && shopt -u extglob
	(( 0 == ${#COMPREPLY} )) && COMPREPLY+=("")
}

complete -o default -o nospace -F __litp_complete litp
# vim:ts=4:sw=4:ft=sh
