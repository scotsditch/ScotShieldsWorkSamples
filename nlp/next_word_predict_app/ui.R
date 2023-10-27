
library(shiny)

shinyUI(
  pageWithSidebar(
    headerPanel("Capstone Final Project-Predict Next Word"),
    
    sidebarPanel(
      textInput("phrase", label = "Enter incomplete phrase:", value=""),
      actionButton('submit', 'submit'),
      
      h4("Instructions:"),
      p("Please enter an incomplete phrase and then press 'submit' button.  The predicted word to complete the phrase will then appear on the right.")
    ),
    
    mainPanel(
      h4("Predicted Next Word:"),
	  textOutput('result')
    )        
  )
)