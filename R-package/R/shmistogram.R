SegmentShmistogram = R6::R6Class(
    "SegmentShmistogram",
    public = list(
        data = NULL,
        DT = NULL,
        share = NULL,
        n_data_types = NULL,
        initialize = function(data){
            shm = pyshmistogram$Shmistogram(data)
            self$unpack_data(shm)
        },
        unpack_data = function(shm){
            crowd = shm$bins
            loners_data = shm$loners$df2R()
            loners = loners_data$df
            n = list(
                loners = sum(loners$n_obs),
                crowd = sum(crowd$freq),
                na = loners_data$missing
            )
            n$n = n$loners + n$crowd
            self$data = list(
                n = n,
                crowd = crowd,
                loners = loners
            )
            n_all = self$data$n$n + self$data$n$na
            self$share = list(
                loners = self$data$n$loners/n_all,
                crowd = self$data$n$crowd/n_all,
                missing = self$data$n$na/n_all
            )
            self$n_data_types = sum(self$share > 0)
        },
        plot = function(legend=TRUE, loner_axis=TRUE, ...){
            DT = data.table::data.table(self$data$crowd)
            N = nrow(DT)
            if(N == 0){
                print("This data is 100% loners!")
                print(self$data$loners)
                return()
            }
            if(self$n_data_types < 2) legend=FALSE
            xmin = DT$lb[1]
            xmax = DT$ub[N]
            max_rate = max(DT$rate)
            ymax=max_rate
            if(legend){  # leave space for legend bar
                ymax=ymax*1.11
            }
            N_loners = length(self$data$loners$n_obs)
            if(N_loners==0) loner_axis=FALSE
            if(loner_axis) par(mar=c(5, 4, 4, 4) + 0.3)
            plot(x=c(xmin, xmax), y=c(0, ymax),
                type='n', bty='n',
                xlab='values', ylab='crowd frequency rate',
                main='Shmistogram',
                ...
            )
            if(legend) self$add_legend_bar(max_rate, xmin, xmax)
            # Plot crowd
            for(k in 1:N){
                rect(
                    DT$lb[k], 0,
                    DT$ub[k], DT$rate[k],
                    col = 'grey', border=NA
                )
            }
            # Plot loners
            if(N_loners > 0){
                max_loner = max(self$data$loners$n_obs)
                for(k in 1:N_loners){
                    value = self$data$loners$index$values[k]
                    n_obs = as.numeric(self$data$loners$n_obs)[k]
                    y_obs = max_rate*n_obs/max_loner
                    segments(x0=value, y0=0, x1=value, y1=y_obs,
                        col='red', lwd=2)
                    points(x=value, y=y_obs, pch=16, cex=0.6, col='red')
                }
                if(loner_axis){
                    par(new = TRUE)
                    lonery = c(0, max_loner*1.11)
                    plot(x=c(xmin, xmax), y=lonery, 
                        type = "n", axes = FALSE, 
                        bty = "n", xlab = "", ylab = "")
                    axis(side=4, at=pretty(c(0, max_loner)), 
                        col='red', col.ticks='red', col.axis='red')
                    mtext("loner frequency", side=4, line=3, col='red')
                }
            }
        },
        add_legend_bar = function(max_rate, xmin, xmax){
            share = self$share
            lymin = max_rate*1.03
            lymid = max_rate*1.07
            xrange = xmax-xmin
            barxl = xmin + 0.08*xrange
            barxr = xmin + 0.92*xrange
            xr1 = barxl + share$loners*(barxr - barxl)
            xr2 = xr1 + share$crowd*(barxr - barxl)
            gcolors = list(
                loners = 'red',
                crowd = 'grey',
                missing = 'black'
            )
            xl = list(
                loners = barxl,
                crowd = xr1,
                missing = xr2
            )
            xr = list(
                loners = xr1,
                crowd = xr2,
                missing = barxr
            )
            myrect = function(...) rect(..., border=NA)
            for(kind in names(share)){
                if(share[[kind]] > 0){
                    myrect(xl[[kind]], lymin, xr[[kind]], lymid, col=gcolors[[kind]])
                }
            }
            which_kinds = names(share)[which(share > 0)]
            nk = length(which_kinds)
            xc = as.list(seq(barxl, barxr, length.out=nk + 2)[2:(nk+1)])
            names(xc) = which_kinds
            xyadj = c(0.5,-0.2)
            k = 1
            for(kind in which_kinds){
                if(k==1){
                    xpos = barxl
                }else if((k==3) | nk==2){
                    xpos = barxr
                }else{
                    xpos = (xl[[kind]] + xr[[kind]])/2
                    if(xpos - barxl < 0.15*xrange){
                        xpos = barxl + 0.15*xrange
                    }else if(barxr - xpos < 0.15*xrange){
                        xpos = barxr - 0.15*xrange
                    }
                }
                text(x=xpos, y=lymid, 
                    labels=kind, col=gcolors[[kind]], adj=xyadj)
                k = k + 1
            }
        }
    )
)

#' Plot a shmistogram
#' 
#' @param data A numeric vector. May contain NA
#' @param ... Args to be passed to graphics::plot
shmistogram = function(data, ...){ #kind='segment',
    # if(kind=='segment'){
    #     rshm = SegmentShmistogram$new(data)
    # }else if(kind=='block'){
    #     rshm = BlockShmistogram$new(data)
    # }else{
    #     stop(paste0("kind = ", kind, " not recognized"))
    # }
    rshm = SegmentShmistogram$new(data)
    rshm$plot(...)
}


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
