"""
Steps:
-get the summer.ai.pem key
-login to the env.host machine and add your public key to the machine's authorized keys

http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html
"""

from fabric.api import local, sudo, run, warn_only, env, lcd, cd
import yaml

with open("serapis/config/default.yaml") as f:
    config = yaml.load(f)

# the user to use for the remote commands
env.user = 'ec2-user'
# the servers where the commands are executed
env.hosts = [config['ec2_ip']]

gitfile = 'serapis.git.zip'
lambdafile = 'serapis.lambda.zip'
lambda_bucket = 'ai.summer.1mwords.test'
lambdafunction = config['lambda_function_name']
corpora = [
    'nltk_data/taggers/averaged_perceptron_tagger/averaged_perceptron_tagger.pickle',
    'nltk_data/tokenizers/punkt/english.pickle'
]


def pack():
    # Make sure machine and dev tools are up to date
    sudo('sudo yum -y update')
    sudo('sudo yum -y upgrade')
    sudo('yum install -y atlas-devel atlas-sse3-devel blas-devel gcc gcc-c++ lapack-devel python27-devel --enablerepo=epel')
    sudo('pip install -U pip')

    with warn_only():
        run('rm ~/wordnik.zip')

    sudo('dd if=/dev/zero of=/swapfile bs=1024 count=1500000')
    sudo('mkswap /swapfile')
    sudo('chmod 0600 /swapfile')
    sudo('swapon /swapfile')

    run('/usr/bin/virtualenv --python /usr/bin/python build --always-copy --no-site-packages')
    run('source build/bin/activate')

    # Order is important here, so let's make sure we've got these right
    run('pip install -U pip')
    run('pip install --use-wheel numpy')
    run('pip install --use-wheel scipy')
    run('pip install --use-wheel sklearn')
    run('pip install --use-wheel pandas')

    with open('requirements.txt') as f:
        for req in f.read().splitlines():
            if req.split("=")[0].lower() not in ('numpy', 'scipy', 'scikit-learn', 'sklearn', 'pandas'):
                run('pip install --use-wheel {}'.format(req))

    for lib in ('lib', 'lib64'):
        # Strip SO files
        run('find "$VIRTUAL_ENV/{}/python2.7/site-packages/" -name "*.so" | xargs strip'.format(lib))
        with cd('$VIRTUAL_ENV/{}/python2.7/site-packages/'.format(lib)):
            run('zip -r -9 -q ~/wordnik.zip *')

    # Get the file back onto our local machine
    local('scp %s@%s:~/wordnik.zip %s' % (env.user, env.hosts[0], lambdafile))
    update()


def install_corpora():
    local("python -m nltk.downloader -d nltk_data {}".format(" ".join(config['nltk_corpora'])))
  

def update():
    # Run tests
    # local("py.test serapis/tests/")

    # Updates code in zip file with current Master without going to EC2 first.
    local('git archive --format=zip HEAD -o %s' % gitfile, capture=False)
    local('unzip -d git_tmp -o -u %s' % gitfile)
    with lcd('git_tmp'):
        local('zip -9r ../%s .' % lambdafile)
    local('zip -9 %s serapis/config/credentials.yaml' % lambdafile)

    for corpus in corpora:
        local('zip -9r {} {}'.format(lambdafile, corpus))
    local('rm -r git_tmp')


def qu():
    local('zip -9 %s lambda_handler.py' % lambdafile)


def deploy():
    # If this says that the function is not found, create it first:
    # aws lambda create-function --region us-east-1 --function-name WordTask --zip-file fileb://wordnik.lambda.zip --handler lambda_handler.handler --runtime python2.7 --timeout 10 --memory-size 512 --role arn:aws:iam::054978852993:role/lambda_basic_execution
    local('aws s3 cp {} s3://{}/{} --profile wordnik'.format(lambdafile, lambda_bucket, lambdafile))
    local('aws lambda update-function-code --region us-east-1 --function-name {} --s3-bucket {} --s3-key {} --profile wordnik'.format(lambdafunction, lambda_bucket, lambdafile))
