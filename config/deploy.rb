set :application, 'lctva'
set :repo_url, 'git@github.com:taddeimania/lctva.git'

# Cap Django Settings
set :django_settings_dir, 'watcher/settings'
set :pip_requirements, 'requirements/base.txt'
set :keep_releases, 5
set :nginx, true
set :compilemessages, true
set :deploy_to, '/var/www/lctva'
set :wsgi_file, 'watcher.wsgi'
set :stage, :production
set :django_settings, 'production'
set :celery_name, 'lctva'

# ask :branch, proc { `git rev-parse --abbrev-ref HEAD`.chomp }

# set :deploy_to, '/var/www/my_app'
# set :scm, :git

# set :format, :pretty
# set :log_level, :debug
# set :pty, true

# set :linked_files, %w{config/database.yml}
# set :linked_dirs, %w{bin log tmp/pids tmp/cache tmp/sockets vendor/bundle public/system}

# set :default_env, { path: "/opt/ruby/bin:$PATH" }
# set :keep_releases, 5

namespace :deploy do

  desc 'Restart application'
  task :restart do
    on roles(:app), in: :sequence, wait: 5 do
      # Your restart mechanism here, for example:
      # execute :touch, release_path.join('tmp/restart.txt')
    end
  end

  after :restart, :clear_cache do
    on roles(:web), in: :groups, limit: 3, wait: 10 do
      # Here we can do anything such as:
      # within release_path do
      #   execute :rake, 'cache:clear'
      # end
    end
  end

  after :finishing, 'deploy:cleanup'

end
