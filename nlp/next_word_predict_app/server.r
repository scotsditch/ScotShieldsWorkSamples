library(shiny)
library(tm)
library(RWeka)
library(stringi)
library(stringr)
library(ggplot2)
library(dplyr)
library(data.table)
load("ngram_model.RData")



pred_word <- function (ngram_model, smpl_phrs, WrdOrd = 3) {
  fragment <- smpl_phrs

  step_1 <- stri_trim_both (unlist (strsplit (fragment, split = "[\\.!?]+")))
  step_1 <- step_1 [nchar (step_1) > 0]
 
  if (length (step_1) == 0)
    step_1 <- ""
 
  step_2 <- stri_trim_both (stri_paste ("Start_@fragment", stri_replace_all_regex (stri_replace_all_regex (stri_trans_tolower (step_1), "[^A-Za-z0-9 ']+", " "), "[[:digit:]]+", "###"), "End_@fragment", sep = " "))

  words <- unlist (strsplit (step_2, split = "[ ]+"))
  words [nchar (words) > 0]

  if (!stri_detect (fragment, regex = ".*[\\.!?][[:blank:]]*$"))
    words <- head (words, -1) 
  
  Next_Word <- NULL
  for (n in sort (ngram_model$N, decreasing = TRUE)) {
    
    if (length (words) >= n-1) {
      
      Next_Word <- ngram_model$ngrams [ Begin_Words == paste (tail (words, n-1), collapse = " "), list (word, WrdOrd)]
      if (nrow (Next_Word) > 0) {
        
        Next_Word <- Next_Word [complete.cases (Next_Word)][WrdOrd <= WrdOrd]
        
        break
      }
    }
  }
  
  return (Next_Word)
}


shinyServer(
   function(input, output){
			output$result = renderText({
										input$submit
											if(input$submit==0)
												return()
											else
										isolate(pred_word(ngram_model,input$phrase)[WrdOrd==1]$word)
										})


						  }
		   )




