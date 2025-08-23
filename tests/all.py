# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda",
        is_folder=True,
        preview=False,
    )
