#
#-----------------------------------------------------------------------
#
# This function processes a list of variable name and value pairs passed
# to it as a set of arguments, starting with the second argument.  We 
# refer to these pairs as argument-value pairs (or "arg-val" pairs for
# short) because the variable names in these pairs represent the names
# of arguments to the script or function that calls this function (which
# we refer to here as the "caller").  The first argument to this func-
# tion being the name of an array that contains a list of valid argument
# names that the caller is allowed to accept.  Each arg-val pair must 
# have the form
#
#   ARG_NAME=VAR_VALUE
#
# where ARG_NAME is the name of an argument and VAR_VALUE is the value 
# to set that argument to.  For each arg-val pair, this function creates
# a global variable named ARG_NAME and assigns to it the value VAR_VAL-
# UE.
#
# The purpose of this function is to provide a mechanism by which a pa-
# rent script, say parent.sh, can pass variable values to a child script
# or function, say child.sh, that makes it very clear which arguments of
# child.sh are being set and to what values.  For example, parent.sh can
# call child.sh as follows:
#
#   ...
#   child.sh arg3="Hello" arg2="bye" arg4=("this" "is" "an" "array")
#   ...
#
# Then child.sh can use this function (process_args) as follows to pro-
# cess the arg-val pairs passed to it:
#
#   ...
#   valid_args=( "arg1" "arg2" "arg3" "arg4" )
#   process_args valid_args "$@"
#   ...
#
# Here, valid_args is an array that defines or "declares" the argument
# list for child.sh, i.e. it defines the variable names that child.sh is
# allowed to accept as arguments.  Its name is passed to process_args as
# the first argument.  The "$@" appearing in the call to process_args 
# passes to process_args the list of arg-val pairs that parent.sh passes
# to child.sh as the second through N-th arguments.  In the example 
# above, "$@" represents:
#
#   arg3="Hello" arg2="bye" arg4=("this" "is" "an" "array")
#
# After the call to process_args in child.sh, the variables arg1, arg2, 
# arg3, and arg4 will be set as follows in child.sh:
#
#   arg1=""
#   arg2="bye"
#   arg3="Hello"
#   arg4=("this" "is" "an" "array")
#
# Note that:
#
# 1) The set of arg-val pairs may list only a subset of the list of arg-
#    uments declared in valid_args; the unlisted arguments will be set
#    to the null string.  In the example above, arg1 is set to the null
#    string because it is not specified in any of the arg-val pairs in
#    the call to child.sh in parent.sh. 
#
# 2) The arg-val pairs in the call to child.sh do not have to be in the
#    same order as the list of "declared" arguments in child.sh.  For 
#    instance, in the example above, the arg-val pair for arg3 is listed
#    before the one for arg2.
#
# 3) An argument can be set to an array by starting and ending the value
#    portion of its arg-val pair with opening and closing parentheses,
#    repsectively, and listing the elements within (each one in a set of
#    double-quotes and separated fromt the next by whitespace).  In the
#    example above, this is done for arg4.
#
# 4) If the value portion of an arg-val pair contains an argument that
#    is not defined in the array valid_args in child.sh, the call to 
#    process_args in child.sh will result in an error message and exit
#    from the caller.
#
#-----------------------------------------------------------------------
#
function process_args() {
#
#-----------------------------------------------------------------------
#
# Save current shell options (in a global array).  Then set new options
# for this script/function.
#
#-----------------------------------------------------------------------
#
  { save_shell_opts; set -u +x; } > /dev/null 2>&1
#
#-----------------------------------------------------------------------
#
# Check arguments.
#
#-----------------------------------------------------------------------
#
  if [ "$#" -lt 1 ]; then

    print_err_msg_exit "\
Incorrect number of arguments specified.  Usage:

  ${FUNCNAME[0]} valid_arg_names_array_name \
                 arg_val_pair1 \
                 ... \
                 arg_val_pairN

where the arguments are defined as follows:

  valid_arg_names_array_name:
  The name of the array containing a list of valid argument names.

  arg_val_pair1 ... arg_val_pairN:
  A list of N argument-value pairs.  These have the form

    arg1=\"val1\" ... argN=\"valN\"

  where each argument name (argI) needs to be in the list of valid argu-
  ment names specified in valid_arg_names_array_name.  Note that not all
  the valid arguments listed in valid_arg_names_array_name need to be 
  set, and the argument-value pairs can be in any order, i.e. they don't
  have to follow the order of arguments listed in valid_arg_names_ar-
  ray_name.
"

  fi
#
#-----------------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------------
#
  local valid_arg_names_array_name \
        valid_arg_names_at \
        valid_arg_names \
        num_valid_args \
        num_arg_val_pairs \
        i valid_arg_name arg_already_specified \
        arg_val_pair arg_name arg_value is_array \
        err_msg cmd_line

  valid_arg_names_array_name="$1"
  valid_arg_names_at="${valid_arg_names_array_name}[@]"
  valid_arg_names=("${!valid_arg_names_at}")
  num_valid_args=${#valid_arg_names[@]}
#
#-----------------------------------------------------------------------
#
# Get the number of argument-value pairs (or arg-val pairs, for short) 
# being passed into this function.  These consist of all arguments 
# starting with the 2nd, so we subtract 1 from the total number of argu-
# ments.
#
#-----------------------------------------------------------------------
#
  num_arg_val_pairs=$(( $# - 1 ))
#
#-----------------------------------------------------------------------
#
# Make sure that the number of arg-val pairs is less than or equal to 
# the number of valid arguments.
#
#-----------------------------------------------------------------------
#
  if [ "${num_arg_val_pairs}" -gt "${num_valid_args}" ]; then
    print_err_msg_exit "\
The number of argument-value pairs specified on the command line (num_-
arg_val_pairs) must be less than or equal to the number of valid argu-
ments (num_valid_args) specified in the array valid_arg_names:
  num_arg_val_pairs = ${num_arg_val_pairs}
  num_valid_args = ${num_valid_args}"
  fi
#
#-----------------------------------------------------------------------
#
# Initialize all valid arguments to the null string.  Note that the 
# scope of this initialization is global, i.e. the calling script or 
# function will be aware of these initializations.  Also, initialize
# each element of the array arg_already_specified to "false".  This ar-
# ray keeps track of whether each valid argument has already been set 
# to a value by an arg-val specification.
#
#-----------------------------------------------------------------------
#
  for (( i=0; i<${num_valid_args}; i++ )); do
    valid_arg_name="${valid_arg_names[$i]}"
    eval ${valid_arg_name}=""
    arg_already_specified[$i]="false"
  done
#
#-----------------------------------------------------------------------
#
# Loop over the list of arg-val pairs and set argument values.
#
#-----------------------------------------------------------------------
#
  for arg_val_pair in "${@:2}"; do

    arg_name=$(echo ${arg_val_pair} | cut -f1 -d=)
    arg_value=$(echo ${arg_val_pair} | cut -f2 -d=)
#
# If the first character of the argument's value is an opening parenthe-
# sis and its last character is a closing parenthesis, then the argument
# is an array.  Check for this and set the is_array flag accordingly.
#
    is_array="false"
    if [ "${arg_value:0:1}" = "(" ] && \
       [ "${arg_value: -1}" = ")" ]; then
      is_array="true"
    fi 
#
#-----------------------------------------------------------------------
#
# Make sure that the argument name specified by the current argument-
# value pair is valid.
#
#-----------------------------------------------------------------------
#
    err_msg="\
The specified argument name (arg_name) in the current argument-value 
pair (arg_val_pair) is not valid:
  arg_val_pair = \"${arg_val_pair}\"
  arg_name = \"${arg_name}\""
    check_var_valid_value "arg_name" "valid_arg_names" "${err_msg}"
#
#-----------------------------------------------------------------------
#
# Loop through the list of valid argument names and find the one that 
# the current arg-val pair corresponds to.  Then set that argument to
# the specified value.
#
#-----------------------------------------------------------------------
#
    for (( i=0; i<${num_valid_args}; i++ )); do

      valid_arg_name="${valid_arg_names[$i]}"
      if [ "${arg_name}" = "${valid_arg_name}" ]; then
#
# Check whether the current argument has already been set by a previous
# arg-val pair on the command line.  If not, proceed to set the argument
# to the specified value.  If so, print out an error message and exit 
# the calling script.
#
        if [ "${arg_already_specified[$i]}" = "false" ]; then
          arg_already_specified[$i]="true"
          if [ "${is_array}" = "true" ]; then
            eval ${arg_name}=${arg_value}
          else
            eval ${arg_name}=\"${arg_value}\"
          fi
        else
          cmd_line=$( printf "\'%s\' " "${@:1}" )
          print_err_msg_exit "\
The current argument has already been assigned a value on the command
line:
  arg_name = \"${arg_name}\"
  cmd_line = ${cmd_line}
Please assign values to arguments only once on the command line."
        fi
      fi

    done

  done
#
#-----------------------------------------------------------------------
#
# Restore the shell options saved at the beginning of this script/func-
# tion.
#
#-----------------------------------------------------------------------
#
  { restore_shell_opts; } > /dev/null 2>&1

}

