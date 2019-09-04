wd <- '/Users/xjtang/Applications/GoogleDrive/Temp/cms/regrow/30m/'
rg <- paste(wd, 'regrow.csv', sep='')
if (!exists('rg2')){
  rg2 <- read.csv(rg, header=T)
}
rg2 <- rg2[rg2[, 'agb15'] > 0,]
rg2 <- rg2[rg2[, 'start'] > 1,]