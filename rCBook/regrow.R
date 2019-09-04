wd <- '/Users/xjtang/Applications/GoogleDrive/Temp/cms/regrow/'
regrow <- paste(wd, 'regrow.csv', sep='')
forest <- paste(wd, 'forest.csv', sep='')

init <- function(){
  rg <<- read.table(regrow, header=T, sep=',', stringsAsFactors=F)
  sf <<- read.table(forest, header=T, sep=',', stringsAsFactors=F)
  sfdb <<- apply(sf[, 8:21], 1, max) - apply(sf[, 8:21], 1, min)
  rg$bmax <<- apply(rg[, 8:21], 1, max)
  rg$bmin <<- apply(rg[, 8:21], 1, min)
  rg$wmax <<- apply(rg[, 8:21], 1, which.max)
  rg$wmin <<- apply(rg[, 8:21], 1, which.min)
  rg$emax <<- apply(rg[, 8:13], 1, max)
  rg$lmax <<- apply(rg[, 14:21], 1, max)
  rg$rmv <<- rg[, 'emax'] - rg[, 'bmin']
  rg$rgw <<- rg[, 'lmax'] - rg[, 'bmin']
}

plot_sfdb <- function(sfdb_=sfdb, des=paste(wd, 'sfdb.png', sep='')){
  sfdb_[sfdb_>200] <- 200
  png(file=des, width=800, height=600, pointsize=16)
  hist(sfdb_, seq(0,200,10), main='', col='cadetblue3', ylab='n', xlab='Delta Biomass (Mg ha-1)', xlim=c(0, 200))
  box(col='black', lwd=1)
  grid(col = "gray70", lty = "dashed", lwd=1)
  dev.off()
}

interp <- function(rg){
  rg <- rg[rg['Fd']<=5,]
  rg <- rg[rg['Flr']<=5,]
  # rg <- rg[rg['Fn']==0,]
  rg <- rg[rg['dbm']>0,]
  
  rg2 <- rg[(rg['Fr']>10)&(rg['Fr']<=20),]
  rg3 <- rg[rg['Fr']>50,]
  rg <- rg[rg['Fr']>33,]
  #rg <- rg[rg['end']==0,]
  
  
  x <- 16-rg[, 'str']
  #y <- rg[, 'dbm'] / rg[, 'Fr']
  y <- rg[, 'dbm']
  x2 <- 16-rg2[, 'str']
  y2 <- rg2[, 'dbm'] / rg2[, 'Fr']
  
  plot(x, y, xlim=c(1,16))
  #points(x2,y2,col='red')
  points(x, y)
}

subrg <- function(rg_=rg){
  rgs <- rg[rg[,'bmin'] <= 50,]
  rgs <- rgs[rgs[,'wmin'] <= 6,]
  rgs <- rgs[rgs[,'rgw'] >= 100,]
  return(rgs)
}

plot_rgc <- function(rgts){
  # png(file=paste(output, des, sep=''), width=1000, height=350, pointsize=16)
  plot(-9999, -9999, ylab='Aboveground biomass (Mg ha-1)', xlab='Yeas of regrow', 
       xlim=c(0, 10), ylim=c(0, 250), bty='n')
  for(i in 1:nrow(rgts)){
    ts <- as.numeric(rgts[i, ])
    start <- 0
    dfst <- 0
    for(j in 1:(length(ts)-1)){
      if((start == 0)&(ts[j + 1] - ts[j] > 20)){start <- j}
      if(ts[j + 1] - ts[j] < -30){dfst <- j}
    }
    if(start > dfst){
      ts <- ts - ts[start]
      lines(0:(length(ts) - start), ts[start:length(ts)], col='azure4', lwd=1)
    }
  }
}

model_rg <- function(d){
  plot(-9999, -9999, ylab='AGB (Mg ha-1)', xlab='Yeas of regrow', 
       xlim=c(0, 10), ylim=c(0, 250), bty='n')
  a <- rep(0, nrow(d))
  for(i in 1:nrow(d)){
    ts <- as.numeric(d[i, 8:21])
    start <- 0
    dfst <- 0
    for(j in 1:(length(ts)-1)){
      if((start == 0)&(ts[j + 1] - ts[j] > 20)){start <- j}
      if(ts[j + 1] - ts[j] < -30){dfst <- j}
    }
    if(start > dfst){
      ts <- ts - ts[start]
      x <- 0:(length(ts) - start)+1
      y <- ts[(start):length(ts)]
      rgm <- lm('y~log(x)+0', data.frame(x, y))
      a[i] <- rgm$coefficients
      y2 <- log(x) * a[i]
      lines(x-1, y2, col='grey70', lwd=1, lty='dashed')
      points(x-1, y,col='grey70', pch=20,cex=0.8)
      cat(i)
    }
  }
  a <- a[a>0]
  a2 <- mean(a)
  y3 <- a2*log(x)
  lines(x-1, y3, col='darkolivegreen4', lwd=2)
  return(a)
}

# end