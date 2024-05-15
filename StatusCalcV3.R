# HYDROSOS LAKE VICTORIA BASIN WORKSHOP
# script to calculate hydrological status from flow data
# Katie Facer-Childs 15-08-2023

### PARTICIPANTS WILL NEED TO EDIT LINES 14,15,16, (possibly 27 & 79), 88,89

# set working directory (you'll need to replace \ with / if you copy the path)
#setwd("./")

################################# PREPARATION #################################

# read in catchment list
#stations<-read.csv("stations.csv")
stationid<-39001
input_directory<-"./example_data/input/"
output_directory<-"./example_data/output_R/"

# read in flow data
#flowdata<-read.csv(paste0(stationid,".csv"))
flowdata<-read.csv(sprintf("%s%s.csv", input_directory,stationid))           

#set the column names
colnames(flowdata)<-c("date","flow")
# format the date column (this might cause difficulties, please look at the 
# date as it appears in the column and amend the format accordingly 
# e.g. 1991-02-30 would be "%Y-%m-%d")
flowdata$date<-as.Date(flowdata$date,format="%d/%m/%Y")

### check the timeseries is complete (sequential) - we need missing data to be
### set as NAs, not missing from the dataset

if (length(flowdata$date)!=as.numeric(max(flowdata$date)-min(flowdata$date))){
  fulldata<-data.frame(date=c(as.Date(seq(min(flowdata$date),max(flowdata$date),by=1),format="%Y-%m-%d")))
  flowdata<-merge(fulldata,flowdata,by="date",all.x=T)
}

flowdata$date<-as.Date(flowdata$date)

#make a month and a year column
flowdata$month<-as.numeric(format(flowdata$date,format="%m"))
flowdata$year<-as.numeric(format(flowdata$date,format="%Y"))

# plot the daily timeseries
plot(flowdata$date,flowdata$flow, type="l",xlab="Date",ylab="flow (cumecs)")

# is the data long enough to calculate a Long Term Average?
startYear<-min(flowdata$year)
endYear<-max(flowdata$year)
print(paste0("there are ",endYear-startYear," years of data in this file"))
# how much is missing data?
navals<-sum(is.na(flowdata$flow))
flowlength<-length(flowdata$flow)
print(paste0("there are ",navals, " missing values, which is ", 
             sprintf((navals/flowlength)*100,fmt='%#.2f'), "% missing")) 

# is there too much missing data for any particular month? 

# this counts the non-NA values in each month-year, 
# divides it by the length of the month, 
# and multiplies it by 100 to get the percent complete

# we will use this to set months with less than 50% completeness to NA
flowcompleteness<-aggregate(flow ~ month + year, flowdata, 
                            FUN=function(x) ((sum(!is.na(x)))/(length(x)))*100,
                            na.action=NULL)
colnames(flowcompleteness)<-c("month","year","pc_complete")


## FUTURE STEP - INFILLING MISSING DATA

##################### STEP 1 CALCULATE MONTHLY MEAN FLOWS #####################

mon_flow<-aggregate(flow ~ month + year, flowdata,
                    FUN=mean, na.rm=TRUE, na.action=NULL)
# set those NA values where the months are too incomplete
mon_flow$flow[which(flowcompleteness$pc_complete<50)]<-NaN

# plot monthly data
mon_flow$date<-as.Date(paste0("01-",mon_flow$month,"-",mon_flow$year),
                       format="%d-%m-%Y")
plot(mon_flow$date,mon_flow$flow, type="l",xlab="Date",ylab="flow (cumecs)")

######## STEP 2 CALCULATE MONTHLY MEAN FLOWS AS A PERCENT OF AVERAGE #########

# here we will use 1991-2020, you will need to edit these dates if this is not
# suitable for your data

stdStart<-1991
stdEnd<-2020

# again let's do some completeness checks

LTAcheck<-aggregate(flow ~ month, 
                    mon_flow[which(mon_flow$year==stdStart & mon_flow$month==1):
                             which(mon_flow$year==stdEnd & mon_flow$month==12),],
                    FUN=function(x) sum(!is.na(x)),
                    na.action=NULL)
print(LTAcheck)

# how close to 30 years do you have for each month of the year?!

# calculate the long term average (LTA) for each calendar month
LTAdata<-aggregate(flow ~ month, 
                   mon_flow[which(mon_flow$year==stdStart & mon_flow$month==1):
                              which(mon_flow$year==stdEnd & mon_flow$month==12),],
                   FUN=mean, na.rm=TRUE, na.action=NULL)


# use this as a look up to calculate each month as a percent of average
# (this is called a "for loop")
mon_flow$flowperc<-NA

flowpercfun<-  function(x) (mon_flow$flow[x]/LTAdata$flow[which(LTAdata$month==mon_flow$month[x])])*100
mon_flow$flowperc<-unlist(lapply(1:length(mon_flow$flow),FUN=flowpercfun))

# another plot check
plot(mon_flow$date,mon_flow$flowperc, type="l",xlab="Date",ylab="Flow as % average")


###################### STEP 3 CALCULATE RANK PERCENTILES ######################

# rank percentile uses the Weibull distribution to rank the month 
# against the historic data
# i/N+1 (where i is the rank of the current month and N is the number of months 
# in the period of record)

mon_flow$rank<-NA
mon_flow$rankperc<-NA

for (imonth in 1:12){
  mon_flow$rank[which(mon_flow$month==imonth)]<-rank(mon_flow$flowperc[which(mon_flow$month==imonth)], na.last='keep')
}

for (imonth in 1:12){
  mon_flow$rankperc[which(mon_flow$month==imonth)]<-mon_flow$rank[which(mon_flow$month==imonth)]/(sum(!is.na(mon_flow$flow[which(mon_flow$month==imonth)]))+1)
}

# set the NA values as rank NA
mon_flow$rank[is.na(mon_flow$flow)]<-NaN
mon_flow$rankperc[is.na(mon_flow$flow)]<-NaN

# plot again
plot(mon_flow$date,mon_flow$rankperc, type="l",xlab="Date",ylab="Rank Percentile")


####################### STEP 4 ASSIGN STATUS CATEGORIES #######################

# set up percentile categories
# NOTE THESE ARE LIKELY TO BE CHANGED TO BE MORE "STANDARD" SOON
pc_cat<-data.frame(
  category=c("low","below_normal","normal","above_normal","high"),
  lowerlim=c(0,0.13001,0.28001,0.72,0.87),
  upperlim=c(0.13,0.28,0.71999,0.86999,1),
  hexcolour=c("#CD233f","#FFA883","#E7E2BC","#8ECEEE","#2C7DCD")
)

catlookup <- function (x) ifelse(is.na(mon_flow$rankperc[x]),
                                 NaN,
                                 which(mon_flow$rankperc[x] >= pc_cat$lowerlim & mon_flow$rankperc[x] <= pc_cat$upperlim))


mon_flow$flowcat<-unlist(lapply(1:length(mon_flow$flow),FUN=catlookup))
mon_flow$catname<-pc_cat[mon_flow$flowcat,1]
# print the last few values
print(tail(mon_flow$catname))

mon_flow$hexcolour<-as.character(pc_cat[mon_flow$flowcat,4])
barplot(tail(mon_flow$flowperc) ~ tail(mon_flow$date),col=(tail(mon_flow$hexcolour)),xlab="Date",ylab="Flow Percentile")


##################### STEP 5 WRITE OUT DATA FOR THE PORTAL #####################

outData<-data.frame(
  date=as.Date(mon_flow$date,format="%Y-%m-%d"),
  flowcat=mon_flow$flowcat)
write.csv(outData,sprintf("%scat_%s.csv", output_directory,stationid),row.names=F)

