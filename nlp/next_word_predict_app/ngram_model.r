
library(tm)
library(RWeka)
library(stringi)
library(stringr)
library(ggplot2)
library(dplyr)
library(data.table)


EndWord <- function (text) {

    words <- unlist (strsplit (text, split = "[ ]+"))
    words<-words [nchar (words) > 0]
    words [length (words)]
}

StartingWords <- function (text) {

    words <- unlist (strsplit (text, split = "[ ]+"))
    words<-words [nchar (words) > 0]
    BeginWords <- words [1:length (words)-1]
    paste (BeginWords, collapse = " ")
}

setwd("~/Coursera DS/Capstone/Data")

file1 <- file("final/en_US/en_US.blogs.txt", "rb")
blogs <- readLines(file1, n=1000, encoding="UTF-8")
close(file1)

file2 <- file("final/en_US/en_US.news.txt", "rb")
news <- readLines(file2, n=1000, encoding="UTF-8")
close(file2)

file3 <- file("final/en_US/en_US.twitter.txt", "rb")
twitter <- readLines(file3, n=1000, encoding="UTF-8")
close(file3)

set.seed(1)
blogsSample <- sample(blogs, length(blogs)*0.25)
newsSample <- sample(news, length(news)*0.25)
twitterSample <- sample(twitter, length(twitter)*0.25)
twitterSample <- sapply(twitterSample, 
                        function(row) iconv(row, "latin1", "ASCII", sub=""))

text_sample2  <- c(blogsSample,newsSample,twitterSample)

text_sample2 <-tm_map(tm_map(tm_map(tm_map(tm_map(VCorpus(VectorSource(text_sample2)), content_transformer(function(x, pattern) gsub(pattern, " ", x)), "/|@|\\|"), content_transformer(tolower)), removeNumbers), removePunctuation), stripWhitespace)

tdmR <- removeSparseTerms(TermDocumentMatrix(text_sample2, control=list(tokenize=function(x) NGramTokenizer(x, Weka_control(min=1, max=3)))), 0.9999)
freqR_Table<-as.data.table(data.frame(word=names(sort(rowSums(as.matrix(tdmR)), decreasing=TRUE)), freq=sort(rowSums(as.matrix(tdmR)), decreasing=TRUE)))
freqR_Prob3<-freqR_Table[, LastWord    := EndWord (as.character(word)),        by = word][, Begin_Words := StartingWords (as.character(word)), by = word]

    Begin_Words <- freqR_Prob3 [, sum (freq), by = Begin_Words]
    setnames (Begin_Words, c("Begin_Words", "Begin_Words_freq"))

    setkeyv (Begin_Words, "Begin_Words")
    setkeyv (freqR_Prob3, "Begin_Words")
    freqRgram <-freqR_Prob3 [Begin_Words, p := freq / Begin_Words_freq]

setnames(freqRgram,"word","fragment")
setnames(freqRgram,"LastWord","word")

N=1:3

freqRgram <- freqRgram [ freq >= 1, list (fragment, Begin_Words, word, p) ]

freqRgram [, n := unlist (lapply (stri_split (fragment, regex = paste0 ("[", ' \r\n\t.,;:\\"()?!', "]+")), length)) ]
freqRgram <- freqRgram [ order (Begin_Words, -p)]
freqRgram [, WrdOrd := 1:.N, by = Begin_Words]
freqRgram <- freqRgram [ WrdOrd <= 3 ]

model1 <- list (ngrams      = freqRgram,
               N           = N,
               freq_min = 1,
               WrdOrd_max = 3)
class (model1) <- "ngram"

save(ngram_model, file="ngram_model.RData")

