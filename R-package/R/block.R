# # Failed concept:
# BlockShmistogram = R6::R6Class(
#     "BlockShmistogram",
#     public = list(
#         data = NULL,
#         DT = NULL,
#         crooked_root_c = NULL,
#         initialize = function(data){
#             #stopifnot("shmistogram.Shmistogram" %in% class(shm))
#             shm = pyshmistogram$Shmistogram(data)
#             self$unpack_data(shm)
#             if((self$data$n$loners > 0) & (self$data$n$crowd > 0)){
#                 self$blend()
#             }else if(self$data$n$loners > 0){
#                 self$stats_loners()
#             }else{
#                 self$stats_crowd()
#             }
#         },
#         unpack_data = function(shm){
#             crowd = shm$bins
#             loners_data = shm$loners$df2R()
#             loners = loners_data$df # reticulate::py_to_r()
#             n = list(
#                 loners = sum(loners$n_obs),
#                 crowd = sum(crowd$freq),
#                 na = loners_data$missing
#             )
#             n$n = n$loners + n$crowd
#             self$data = list(
#                 n = n,
#                 crowd = crowd,
#                 loners = loners
#             )
#         },
#         stats_loners = function(){
#             stop("TODO")
#         },
#         stats_crowd = function(){
#             stop("TODO")
#         },
#         insert_loner = function(k){
#             value = self$data$loners$index$values[k]
#             n_obs = as.numeric(self$data$loners$n_obs)[k]
#             idx=self$DT[J(value), on='lb', roll=TRUE, which=TRUE]
#             # rectangular roots:
#             # 1. x1*x2 = value
#             # 2. x1/x2 = C
#             #   -> x1 = Cx2
#             #   -> x2*x2 = value/C
#             #   -> x2 = sqrt(value/C)
#             width = sqrt(n_obs/self$crooked_root_c)
#             depth = self$crooked_root_c*width
#             newbin = data.table::data.table(
#                 freq=n_obs,
#                 lb=value,
#                 ub=value,
#                 width=width,
#                 rate=depth,
#                 kind='loner')
#             setattr(self$DT, "sorted", "lb")
#             if(is.na(idx)){ # then value < DT$lb[1]
#                 newbin$pos = self$DT$pos[1] - width
#                 self$DT = rbind(newbin, self$DT)
#                 self$DT$pos = self$DT$pos + width
#             }else if(value > last(self$DT$ub)){
#                 newbin$pos = last(self$DT$pos) + last(self$DT$width)
#                 self$DT = rbind(self$DT, newbin)
#             }else{
#                 DT1 = self$DT[1:idx,]
#                 w1 = value - DT1$lb[idx]
#                 DT1$ub[idx] = DT1$lb[idx] + w1
#                 DT1$freq[idx] = (w1/DT1$width[idx])*DT1$freq[idx]
#                 DT1$width[idx] = w1
#                 newbin$pos=last(DT1$pos) + w1
#                 DT2 = self$DT[idx:nrow(self$DT),]
#                 DT2$lb[1] = DT1$ub[idx]
#                 w2 = DT2$ub[1] - value
#                 DT2$freq[1] = (w2/DT2$width[1])*DT2$freq[1]
#                 DT2$width[1] = w2
#                 DT2$pos = DT2$pos + newbin$width
#                 DT2$pos[1] = DT2$pos[1] + w1
#                 self$DT = rbind(DT1, newbin, DT2)
#             }
#         },
#         blend = function(){
#             self$DT = data.table::data.table(self$data$crowd)
#             self$DT$kind = 'crowd'
#             self$DT$pos = self$DT$lb - self$DT$lb[1]
#             ratios = self$DT$rate/self$DT$width
#             self$crooked_root_c = median(ratios)
#             for(k in 1:length(self$data$loners$n_obs)){
#                 self$insert_loner(k)
#             }
#         },
#         plot = function(){
#             DT = data.table::copy(self$DT)
#             N = nrow(DT)
#             color_lookup = list(
#                 crowd='grey',
#                 loner='pink'
#             )
#             plot(
#                 x=c(DT$pos[1], DT$pos[N] + DT$width[N]),
#                 y=c(0, max(DT$rate))*1.1,
#                 type='n', bty='n',
#                 xlab='Values', ylab='Frequency rate'
#             )
#             for(k in 1:N){
#                 rect(
#                     DT$pos[k], 0,
#                     DT$pos[k] + DT$width[k], DT$rate[k],
#                     col = color_lookup[[DT$kind[k]]]
#                     #, border=NA
#                 )
#             }
# 
#         }
#     )
# )
