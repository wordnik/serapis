"""
Steps:
-get the summer.ai.pem key
-login to the env.host machine and add your public key to the machine's authorized keys

http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html
"""

from fabric.api import *
import time

# the user to use for the remote commands
env.user = 'ec2-user'
# the servers where the commands are executed
env.hosts = ['52.91.194.132']

gitfile = 'wordnik.git.zip'

def pack():
    # create a new source distribution zipfile
    local('git archive --format=zip HEAD -o %s' %gitfile, capture=False)

def deploy():
    # Make sure machine and dev tools are up to date
    sudo('sudo yum -y update')
    sudo('yum -y upgrade')
    sudo('yum -y install python27-devel python27-pip gcc libjpeg-devel zlib-devel gcc-c++')
    
    
    # upload the source zipfile to the temporary folder on the server
    deploy_filename = '/tmp/wordnik.%s.zip' %str(time.time())
    put(gitfile, deploy_filename)
    
    # create a place where we can unzip the zipfile, then enter
    # that directory and unzip it
    with warn_only():
        run('rm -rf ~/lambda')
    run('mkdir ~/lambda')
    with cd('~/lambda'):
        run('unzip %s' %deploy_filename)
        # now setup the package with our virtual environment's
        # python interpreter
        # run('/var/www/yourapplication/env/bin/python setup.py install')
        
        """
        TODO: compile all the dependencies locally on the ec2 machine,
        making sure any extensions are in a subdirectory of ~/lambda so that they are zipped
        """
        run('virtualenv venv')
        run('source venv/bin/activate && pip install -r requirements.txt')
        
        run('zip -9r wordnik.zip *')
    # # now that all is set up, delete the folder again
    # run('rm -rf /tmp/yourapplication /tmp/yourapplication.tar.gz')
    # # and finally touch the .wsgi file so that mod_wsgi triggers
    # # a reload of the application
    # run('touch /var/www/yourapplication.wsgi')
    
    lambdafile = 'wordnik.lambda.zip'
    lambdafunction = 'TestLambdaFunction'
    local('scp %s@%s:~/lambda/wordnik.zip %s' %(env.user, env.hosts[0], lambdafile))
    
    cwd = local('pwd', capture=True).strip()
    local('aws lambda update-function-code --function-name %s --zip-file fileb://%s/%s' %(lambdafunction, cwd, lambdafile))
    
    
    
    
    
    
    
    
    
    
    
    
    