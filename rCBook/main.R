source('/Users/xjtang/Applications/GitHub/CBookie/rCBook/plotting.R')

datafile <- '/Users/xjtang/Applications/Dropbox/CMS/data/regrow_biomass.csv'
output <- '/Users/xjtang/Applications/Dropbox/CMS/data/'
pixel <- '/Users/xjtang/Applications/Dropbox/CMS/data/pixels/deforest.csv'

biomass <- read.table(datafile, header=T, sep=',', stringsAsFactors=F)
biomass2 <- biomass[biomass[, 2] > 5, ]
biomass3 <- biomass2[biomass2[, 1] >= 350, ]

carbon <- read.table(pixel, header=T, sep=',', stringsAsFactors=F)

plot1 <- function(des){
  plot_scatter(biomass3[,2],biomass3[,3],biomass3[,1],paste(des,'regrow_biomass.png',sep=''),title='Regrowth Biomass',axis_name=c('Start of regrowth','Biomass'),y_limit=c(50,400),x_limit=c(2000,2015))
  plot_boxes(biomass3[,2],biomass3[,3],paste(des,'regrow_biomass_box.png',sep=''), title='Regrowth Biomass', axis_name=c('Start of regrowth','Biomass'))
  return(0)
}

plot2 <- function(ori, des){
  d <- read.table(ori, header=T, sep=',', stringsAsFactors=F)
  plot_lines(d, des, 'Pools', c('Date', 'Biomass'), c(0, 300), c(1995, 2015))
  return(0)
}

plot2_all <- function(){
  plot2('/Users/xjtang/Applications/Dropbox/CMS/data/pixels/deforest.csv', paste(output, 'deforest.png', sep=''))
  plot2('/Users/xjtang/Applications/Dropbox/CMS/data/pixels/forest.csv', paste(output, 'forest.png', sep=''))
  plot2('/Users/xjtang/Applications/Dropbox/CMS/data/pixels/regrow.csv', paste(output, 'regrow.png', sep=''))
  return(0)
}

plot_scatter <- function(x, y, z, des, title='Title', axis_name=c('X','Y'), y_limit=0, x_limit=0){
  pcex <- 1.6
  cr_range <- c(min(z), max(z))
  cr <- rev(rainbow((cr_range[2] - cr_range[1] + 1), end = 4 / 6))
  png(file=des, width=1500, height=1500, pointsize=20)
  layout(t(1:2), widths=c(6, 1))
  par(mar=c(4, 4, 1, 0.5))
  plot(-9999, -9999, main=title, ylab=axis_name[1], xlab=axis_name[2], xlim=x_limit, ylim=y_limit, lwd=8, bty='n')
  box(col='black', lwd=1)
  points(x, y, col=cr[round(z - cr_range[1] + 1)], pch=16, cex=pcex)
  par(mar=c(20,5,20,2.5))
  image(y=cr_range[1]:cr_range[2], z=t(cr_range[1]:cr_range[2]), ylab='', col=cr, axes=F, main='', cex.main=.8)
  axis(4, cex.axis=0.8, mgp=c(0, .5, 0))
  dev.off()
  return(lm(y ~ x))
}


plot_boxes <- function(x, y, des, title='Title', axis_name=c('X','Y')){
  pcex <- 1.6
  png(file=des, width=1500, height=1500, pointsize=20)
  r <- cbind(x=x,y=y)
  boxplot(y~x,data=r,main=title,xlab=axis_name[1], ylab=axis_name[2])
  dev.off()
  return(0)
}

plot_lines <- function(data, des, title='Title', axis_name=c('X','Y'), y_limit=0, x_limit=0){
  png(file=des, width=2000, height=1500, pointsize=20)
  plot(-9999, -9999, main=title, ylab=axis_name[1], xlab=axis_name[2], xlim=x_limit, ylim=y_limit, lwd=8, bty='n')
  box(col='black', lwd=1)
  for(i in 2:ncol(data)){
    data2 <- data[data[, i] > 0, ]
    x <- floor(data2[, 1] / 1000) + (data2[, 1] - floor(data2[, 1] / 1000) * 1000) / 365.25
    y <- data2[, i]
    if(grepl('*above*', colnames(data)[i])){
      line_col <- 'blue'
    }else if(grepl('*burned*', colnames(data)[i])){
      line_col <- 'red'
    }else{
      line_col <- 'green4'
    }
    lines(x, y, col=line_col, lwd=2)
  }
  dev.off()
  return(0)
}
