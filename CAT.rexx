/* REXX */
/**********************************************************************/
/* SCRIPT: CAT                            */
/* */
/* DESC:  Emulates the basic functionality of the Linux 'cat'    */
/* command. It concatenates one or more datasets and prints  */
/* them to the default output stream (the terminal).     */
/* */
/* USAGE: From TSO or the ISPF command shell (option 6):       */
/* CAT my.data.set 'another.dataset(member)'         */
/* */
/* If no datasets are given, it reads from standard input   */
/* until the input stream is closed.             */
/**********************************************************************/

/* Parse all arguments (the list of datasets) into a single variable */
ARG dslist

/* --- Case 1: No arguments. Read from standard input (SYSIN). --- */
IF dslist = '' THEN DO
 /* Loop forever, reading from the default input stream */
 DO FOREVER
 PULL line  /* PULL reads a line from the input stack or terminal */
 SAY line  /* SAY writes the line to the default output stream */
 END
END

/* --- Case 2: One or more dataset names were provided. --- */
ELSE DO
 /* Define a standard DDNAME (Data Definition Name) for file operations */
 ddname = 'INFILE'

 /* Loop through each word (dataset name) in the argument list */
 DO i = 1 TO WORDS(dslist)
 dsn = WORD(dslist, i) /* Get the current dataset name */

 /* Attempt to allocate the dataset for shared (read-only) access. */
 /* REUSE allows us to use the same ddname again in the loop.   */
 ADDRESS TSO "ALLOCATE FILE("ddname") DATASET('"dsn"') SHR REUSE"

 /* Check if the allocation was successful (Return Code = 0) */
 IF rc = 0 THEN DO
 /* Read the entire dataset into a stem variable named 'line.' */
 /* The number of lines read is stored in line.0       */
 ADDRESS TSO "EXECIO * DISKR" ddname "(STEM line."

 /* Loop through the lines that were read into the stem variable */
 DO j = 1 TO line.0
 SAY line.j /* Print each line to the terminal */
 END
 END
 ELSE DO
 /* If allocation failed, print a user-friendly error message */
 SAY "CAT: ERROR! Could not allocate dataset:" dsn
 SAY "    TSO ALLOCATE command returned code:" rc
 END
 END /* End of loop for each dataset */

 /* It's good practice to clean up by freeing the allocated DDNAME */
 ADDRESS TSO "FREE FILE("ddname")"
END

EXIT 0
