"""
For CommonsCloud copyright information please see the LICENSE document
(the "License") included with this software package. This file may not
be used in any manner except in compliance with the License

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


"""
Import Flask Dependencies
"""
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from flask.ext.security import current_user
from flask.ext.security import login_required

"""
Import CommonsCloudAPI Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.user import User

from . import module


"""
Basic route for currently logged in user
"""
@module.route('/', methods=['GET'])
def index():
  return redirect(url_for('user.user_profile_get')), 301

@module.route('/v2/user/me.<string:extension>', methods=['OPTIONS'])
def user_me_preflight(extension):
    return status_.status_200(), 200

@module.route('/v2/users.<string:extension>', methods=['OPTIONS'])
def users_preflight(extension):
    return status_.status_200(), 200

@module.route('/v2/users/<int:user_id>.<string:extension>', methods=['OPTIONS'])
def user_get_preflight(user_id, extension):
    return status_.status_200(), 200

@module.route('/v2/applications/<int:application_id>/users.<string:extension>', methods=['OPTIONS'])
def application_users_preflight(application_id, extension):
  return status_.status_200(), 200

@module.route('/v2/templates/<int:template_id>/users.<string:extension>', methods=['OPTIONS'])
def templates_users_preflight(template_id, extension):
    return status_.status_200(), 200

@module.route('/v2/user/me.<string:extension>', methods=['GET'])
@oauth.require_oauth('user')
def user_me(oauth_request, extension):

  User_ = User()
  User_.current_user = oauth_request.user

  arguments = {
    'the_content': User_.current_user,
    'exclude_fields': ['password'],
    'last_modified': 0,
    'expires': 0,
    'max_age': 0,
    'extension': extension
  }

  return User_.endpoint_response(**arguments)


@module.route('/v2/users.<string:extension>', methods=['GET'])
@oauth.require_oauth('user')
def user_list(oauth_request, extension):

  User_ = User()
  user_list = User_.user_list()

  arguments = {
    'the_content': user_list,
    'list_name': 'users',
    'last_modified': 0,
    'expires': 0,
    'max_age': 0,
    'extension': extension
  }

  return User_.endpoint_response(**arguments)


@module.route('/v2/users/<int:user_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth('user')
def user_get(oauth_request, user_id, extension):

  User_ = User()
  this_user = User_.user_get(user_id)

  arguments = {
    'the_content': this_user,
    'extension': extension
  }

  return User_.endpoint_response(**arguments)

@module.route('/v2/applications/<int:application_id>/users.<string:extension>', methods=['GET'])
@oauth.require_oauth('applications')
def application_users(oauth_request, application_id, extension):

  User_ = User()
  User_.current_user = oauth_request.user

  application_users = User_.application_users(application_id)

  if type(application_users) is tuple:
    return application_users

  arguments = {
    'the_content': application_users,
    'list_name': 'users',
    'extension': extension
  }

  return User_.endpoint_response(**arguments)


@module.route('/v2/templates/<int:template_id>/users.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def template_users(oauth_request, template_id, extension):
  
  User_ = User()
  User_.current_user = oauth_request.user

  template_users = User_.template_users(template_id)

  if type(template_users) is tuple:
    return template_users

  arguments = {
    'the_content': template_users,
    'list_name': 'users',
    'extension': extension
  }

  return User_.endpoint_response(**arguments)



"""





VIEWS BELOW HERE ARE SPECIFIC TO THE ACTUAL API AND ARE SERVED AS RENDERED PAGES
NOT AS JSON/GEOJSON API ENDPOINTS.





"""

@module.route('/account/create/success/', methods=['GET'])
def account_creation_success():
  return render_template('security/register-success.html'), 200


@module.route('/user/profile/', methods=['GET'])
@login_required
def user_profile_get():

  user_ = User()
  this_user = user_.user_get(current_user.id)

  return render_template('user/profile.html', user=this_user), 200


# @module.route('/user/remove/', methods=['GET', 'POST'])
# @login_required
# def user_remove():
#   return render_template('user/remove.html', user=current_user), 200


@module.route('/user/profile/', methods=['POST'])
@login_required
def user_profile_post():

  user_ = User()
  user_.user_update(request.form)

  flash('You\'re profile was updated successfully', 'success')

  return redirect(url_for('user.user_profile_get')), 301

