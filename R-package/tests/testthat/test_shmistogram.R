context("Basic shmistogram calls")

set.seed(0)
unif = runif(n=100, min=-10, max=100)
multi = c(rep(0, 20), rep(42, 10), rep(NA, 2))
data = c(unif, multi)
shm = shmistogram::shmistogram(data, return_data=TRUE)
dev.off()

test_that("binning with default parameters gives fixed result", {
    expect_equal(("data" %in% names(shm)), TRUE)
    expect_equal(shm$data$n$loners, 30)
    expect_equal(nrow(shm$data$crowd), 2)
    expect_equal(ncol(shm$data$crowd), 5)
})
