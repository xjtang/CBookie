library(ggplot2)

workdir <- '/Users/xjtang/Applications/GoogleDrive/Temp/cms/plotting/reports/'
output <- '/Users/xjtang/Applications/GoogleDrive/Temp/cms/results/plots/'

all_cum <- paste(workdir, 'all_cumulate.csv', sep='')
all_year <- paste(workdir, 'all_annual.csv', sep='')
select_cum <- paste(workdir, 'select_cumulate.csv', sep='')
select_year <- paste(workdir, 'select_annual.csv', sep='')
select_track <- paste(workdir, 'track.csv', sep='')

ra_cum <- read.table(all_cum, header=T, sep=',', stringsAsFactors=F)
ra_year <- read.table(all_year, header=T, sep=',', stringsAsFactors=F)
rs_cum <- read.table(select_cum, header=T, sep=',', stringsAsFactors=F)
rs_year <- read.table(select_year, header=T, sep=',', stringsAsFactors=F)
rs_track <- read.table(select_track, header=T, sep=',', stringsAsFactors=F)

a_area <- 518131758 * 30 * 30 / 100 / 100
s_area <- 13755 * 30 * 30 / 100 / 100
sf <- 1000 * 1000

plotCum <- function(d, des, sf){
  d <- d[d[,1]<2014000,]
  x <- floor(d[, 1] / 1000) + (d[, 1] - floor(d[, 1] / 1000) * 1000) / 365.25 - 2000.5
  y1 <- d[, 3] / sf
  y2 <- d[, 4] / sf
  y3 <- d[, 5] / sf
  png(file=paste(output, des, sep=''), width=1000, height=350, pointsize=16)
  # plot(-9999, -9999, ylab='Carbon (Mg C ha-1)', xlab='Year', xlim=c(2000.5, 2014.5), 
  #      ylim=c(-0.1, 1.2), bty='n', axes=F)
  barplot(seq(1,14), width=0.9, space=0.1, col='white', border=NA, axes=F, ylab='Carbon (Mg C ha-1)', 
          xlab='Year', ylim=c(-0.2, 1.2))
  # box(col='black', lwd=1)
  # grid(col = "gray70", lty = "dashed", lwd=1)
  lines(x, y1, col='coral1', lwd=2)
  lines(x, y2, col='chartreuse3', lwd=2)
  lines(x, y3, col='dodgerblue4', lty=5, lwd=2)
  axis(side=1, at=seq(1,14)-0.5, tick=T, labels=F, line=1)
  axis(side=1, at=seq(2,14,4)-0.5, tick=F, labels=seq(2002,2014,4), line=1)
  axis(side=2, at=seq(-0.2,1.2,0.2), tick=T, labels=F)
  axis(side=2, at=seq(0,1.2,0.4), tick=F, labels=seq(0,1.2,0.4))
  lines(c(1.5,14.5), c(0,0), col='gray10', lwd=1, lty=3)
  dev.off()
}

plotYear <- function(d, des){
  x <- d[, 1]
  y1 <- d[, 3] / sf
  y2 <- d[, 4] / sf
  y3 <- d[, 5] / sf
  for(i in nrow(d):2){
    y1[i] = y1[i] - y1[i-1]
    y2[i] = y2[i] - y2[i-1]
    y3[i] = y3[i] - y3[i-1]
  }
  png(file=paste(output, des, sep=''), width=1000, height=500, pointsize=40)
  plot(-9999, -9999, main='Annual Flux', ylab='Carbon (Tg C)', xlab='Year', xlim=c(2000, 2016), ylim=c(-0.5, 0), bty='n')
  # box(col='black', lwd=1)
  # grid(col = "gray70", lty = "dashed", lwd=1)
  lines(x, y1, col='coral1', lwd=2)
  lines(x, y2, col='chartreuse3', lwd=2)
  lines(x, y3, col='dodgerblue4', lty=5, lwd=2)
  dev.off()
}

Year <- rep(2001:2016, each=4)
LC <- rep(c('Forest', 'Crop', 'Regrow', 'Other'), times=16)
Fraction <- rep(0, 4*16)
for(i in 1:16){
  Fraction[i*4-3] <- rs_track[i, 'Forest'] / rs_track[i, 'Total'] * 100
  Fraction[i*4-2] <- rs_track[i, 'Pasture'] / rs_track[i, 'Total'] * 100
  Fraction[i*4-1] <- rs_track[i, 'Regrow'] / rs_track[i, 'Total'] * 100
  Fraction[i*4] <- sum(rs_track[i, c(2,4,5,8,9,10)]) / rs_track[i, 'Total'] * 100
}
area_ts <- data.frame(Year, LC, Fraction)
area_ts$LC <- factor(area_ts$LC, levels = c('Other', 'Regrow', 'Crop', 'Forest'))
#area_ts <- rbind(area_ts[area_ts['LC']=='Forest'], area_ts[area_ts['LC']=='Crop'], area_ts[area_ts['LC']=='Regrow'], area_ts[area_ts['LC']=='Other'])

plotArea <- function(d, des){
  ggplot(d, aes(x=Year, y=Fraction, fill=LC)) + 
    geom_area()
}

plotBar <- function(d, des){
  x <- d[, 1]
  y <- d[, 13]/1000
  png(file=paste(output, des, sep=''), width=1000, height=500, pointsize=24)
  barplot(y[1:14], width=0.9, space=0.1, col='cadetblue3', ylab='Area (1000 ha.)', xlab='Year', 
          ylim=c(0,80))
  # box(col='black', lwd=1)
  # grid(col = "gray70", lty = "dashed", lwd=1)
  axis(side=1, at=seq(1,14)-0.5, tick=T, labels=F, line=1)
  axis(side=1, at=seq(2,14,4)-0.5, tick=F, labels=seq(2002,2014,4), line=1)
  dev.off()
}

plotFlux <- function(d, des, sf){
  ylimit <- c(0, 0.5)
  x <- d[, 1]
  emit <- d[, 3] / sf
  regrow <- d[, 4] / sf
  net <- d[, 5] / sf
  for(i in nrow(d):2){
    emit[i] = emit[i] - emit[i-1]
    regrow[i] = regrow[i] - regrow[i-1]
    net[i] = net[i] - net[i-1]
  }
  png(file=paste(output, des, sep=''), width=1000, height=500, pointsize=24)
  barplot(emit[1:14], width=0.9, space=0.1, col='coral1', 
          ylab='Flux (Mg C / ha. / yr.)', xlab='Year', ylim=ylimit, axes=F)
  par(new=T)
  barplot(regrow[1:14], width=0.9, space=0.1, col='chartreuse3', 
          axes=F, ylim=ylimit)
  lines(seq(1,14)-0.5, net[1:14], col='dodgerblue4',lwd=2,lty=5)
  axis(side=1, at=seq(1,14)-0.5, tick=T, labels=F, line=1)
  axis(side=1, at=seq(2,14,4)-0.5, tick=F, labels=seq(2002,2014,4),line=1)
  axis(side=2, at=seq(0,0.15,0.05), tick=T, labels=F)
  axis(side=2, at=seq(0,0.15,0.05), tick=F, labels=c('0','0.05','0.10','0.15'))
  
  legend(1, 0.4, legend=c('Emission','Regrow','Net','Deforestation'), 
         fill=c('coral1','chartreuse3',NA,'cadetblue3'), 
         border=c(NA,NA,NA,NA),
         col=c(NA,NA,'dodgerblue4',NA), 
         lty=c(NA,NA,5,NA), seg.len=1,
         lwd=c(NA,NA,2,NA), horiz=F, merge=T)
  
  # box(col='black', lwd=1)
  # grid(col = "gray70", lty = "dashed", lwd=1)
  dev.off()
}