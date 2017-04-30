## Basic Forecast Steps

library("forecast")
library("tseries")
library("sqldf")
library("manipulate")
library("caret")
library("qdapTools")
library("RODBC")
library("dplyr")
library("xts")


##Pulling data from sql server

con<-odbcConnect("RsqlConnect")

dataDF<-sqlQuery(con,"select * from Table")


##Filling Gaps in time
library(dplyr)

tseries = seq(as.POSIXct("2015-01-01 00:00:00", tz="America/Los_Angeles"), as.POSIXct("2015-12-31 23:00:00", tz="America/Los_Angeles"), by="hour")

df <- data.frame(FieldDateTime=tseries)
df2<-df
df2$FieldDateTime<-as.POSIXct(df$FieldDateTime,'%Y-%m-%d %H:%M:%S')

## Filling time gaps

filledataDF<-sqldf("select
                  df2.FieldDateTime,
                  median(dataDF.Field1) as MedField1,
                  median(dataDF.Field2) as MedField2,
                  median(dataDF.Field3) as MedField3,
                  median(dataDF.Field4) as MedField4,

                  from df2
                  left outer join dataDF on df2.FieldDateTime = dataDF.FieldDateTime
                  group by df2.FieldDateTime
                  order by df2.FieldDateTime asc")


##Simple Model

##Partitioning Time Series

EndTrain<-3*168
ValStart<-EndTrain+1
ValEnd<-ValStart+20


tsTrain <-filledataDF$MedField1[1:EndTrain]
tsValidation<-filledataDF$MedField1[ValStart:ValEnd]


##BoxCox

Field1lambda <- BoxCox.lambda(tsTrain)

##Predictors
xreg<-filledataDF[,names(filledataDF)!="MedField1"]
xregTrain<-xreg[1:EndTrain,]
xregVal<-xreg[ValStart:ValEnd,]

##Fit Model
Mod1Fit <- auto.arima(tsTrain, lambda = Field1lambda, stepwise=FALSE, approximation = FALSE ) #stepwise & approximation are shortcuts auto.arima uses, setting them to false makes it test more models

##Checking effect of Field2 predictor
Mod2Fit <- auto.arima(tsTrain, lambda = Field1lambda, xreg=xregTrain$Field2, stepwise=FALSE, approximation = FALSE )

##Checking Model Fit
cbind(ModelName<-c("Mod1Fit","Mod2Fit")
      ,rbind(
        Mod1Fit$aicc
        ,Mod2Fit$aicc
      )
)

##Plot Residuals

plot(residuals(Mod1Fit))
Acf(residuals(Mod1Fit))

plot(residuals(Mod2Fit))
Acf(residuals(Mod2Fit))


##Forecast Model
Mod1Cast<-forecast(Mod1Fit, h=20)

Mod2Cast<-forecast(Mod2Fit,xreg=xregVal$Field2, h=20)


##Check Accuracy
cbind(ModelName<-c("Mod1Fit","Mod2Fit")
      ,rbind(
        accuracy(Mod1Cast$mean,tsValidation)
        ,accuracy(Mod2Cast$mean,tsValidation)

      )
)


##Plot

y<-tsValidation
r<-Mod1Cast$mean
s<-Mod2Cast$mean

require(graphics)
require(manipulate)
manipulate({
  lines <- list(if (chk.y) ts(y[x:(x+20)])
                , if(chk.r) ts(r[x:(x+20)])
                , if(chk.s) ts(s[x:(x+20)])

  )
  cols <- c(if (chk.y) "red"
            , if (chk.r) "purple"
            , if (chk.s) "orange"

  )
  do.call(ts.plot, c(lines, list(gpars=list(col=cols, xlab="t", ylab="y"))))
},
chk.y=checkbox(TRUE, "Validation red"),
chk.r=checkbox(TRUE, "Mod1Cast Purple"),
chk.s=checkbox(TRUE, "Mod2Cast orange"),

x=slider(1,length(y))
)
