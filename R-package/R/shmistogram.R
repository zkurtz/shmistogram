default_plotting_params = function(){
    return(list(
        xlab='values',
        ylab='crowd frequency rate',
        main='Shmistogram'
    ))
}

#' A class of methods for generating a shmistogram
#' 
#' @details "Segment" refers to the line segements used to represent
#' the multinomial component of the underlying density model
SegmentShmistogram = R6::R6Class(
    "SegmentShmistogram",
    public = list(
        data = NULL,
        DT = NULL,
        share = NULL,
        n_data_types = NULL,
        initialize = function(data, params=list()){
            self$validate_binning_params(params$binning_params)
            shm = do.call(pyshmistogram$Shmistogram, c(list(x=data), params))
            self$unpack_data(shm)
        },
        validate_binning_params = function(params){
            bp = params$binning_params #possibly NULL, no problem
            if(!is.null(bp$min_data_in_leaf)){
                stopifnot(is.integer(bp$min_data_in_leaf))
            }
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
            args = list(...)
            pp = default_plotting_params()
            for(key in intersect(names(args), names(pp))){
                pp[[key]] = args[[key]]
                args[[key]] = NULL
            }
            DT = data.table::data.table(self$data$crowd)
            LT = reticulate::py_to_r(self$data$loners)
            LT$value = as.numeric(row.names(LT))
            N = nrow(DT)
            if(N == 0){
                print("This data is 100% loners!")
                print(self$data$loners)
                return()
            }
            if(self$n_data_types < 2) legend=FALSE
            xmin = min(DT$lb[1], LT$value[1], na.rm=TRUE)
            xmax = max(DT$ub[N], LT$value[nrow(LT)], na.rm=TRUE)
            max_rate = max(DT$rate)
            ymax=max_rate
            if(legend){  # leave space for legend bar
                ymax=ymax*1.11
            }
            N_loners = length(self$data$loners$n_obs)
            if(N_loners==0) loner_axis=FALSE
            if(loner_axis) par(mar=c(5, 4, 4, 4) + 0.3)
            do.call(plot, c(list(
                x=c(xmin, xmax), 
                y=c(0, ymax),
                type='n', bty='n',
                xlab=pp$xlab, 
                ylab=pp$ylab,
                main=pp$main),
                args)
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
#' @param params List of parameters to pass to the shmistogram
#' constructor
#' @param plotting_params List of parameters passed to the plot call
#' @param return_data (boolean) If TRUE, return the shmistogram data
#' in addition to building the plot
#' 
#' @export
#' 
shmistogram = function(data, 
        params=list(), 
        plotting_params=list(),
        return_data=FALSE
    ){
    rshm = SegmentShmistogram$new(data, params=params)
    do.call(rshm$plot, plotting_params)
    if(return_data) return(rshm)
}
