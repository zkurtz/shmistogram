#
# Following https://cran.r-project.org/web/packages/reticulate/vignettes/package.html
#

# global reference (will be initialized in .onLoad)
pyshmistogram <- NULL

.onLoad <- function(libname, pkgname) {
    # use superassignment to update global reference
    pyshmistogram <<- reticulate::import("shmistogram", delay_load=TRUE)
}