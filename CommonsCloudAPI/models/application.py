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
Import Python Dependencies
"""
import json

from datetime import datetime

from functools import wraps


"""
Import Commons Cloud Dependencies
"""
from CommonsCloudAPI.models.base import CommonsModel

from CommonsCloudAPI.extensions import db
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import sanitize
from CommonsCloudAPI.extensions import status as status_

class UserApplications(db.Model, CommonsModel):

  __public__ = {'default': ['read', 'write', 'is_admin']}

  __tablename__ = 'user_applications'
  __table_args__ = {
    'extend_existing': True
  }

  user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
  application_id = db.Column(db.Integer(), db.ForeignKey('application.id'), primary_key=True)
  read = db.Column(db.Boolean())
  write = db.Column(db.Boolean())
  is_admin = db.Column(db.Boolean())
  applications = db.relationship('Application', backref=db.backref("user_applications", cascade="all,delete"))

  def __init__(self, user_id, application_id, read=True, write=False, is_admin=False):
    self.user_id = user_id
    self.application_id = application_id
    self.read = read
    self.write = write
    self.is_admin = is_admin

  def permission_create(self, application_id, user_id, request_object):

    """
    Before we create the User permissions for this application, we need to make sure that
    the user requesting them is authenticated and has the `is_admin` permission for the
    application_id being requested.
    """
    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Users for Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You are not allowed to view this User\'s permissions because you are not an administrator of this Application'), 401

    permissions_ = json.loads(request_object.data)

    """
    Add the new application to the database
    """
    new_permissions = {
      'user_id': user_id,
      'application_id': application_id,
      'read': sanitize.sanitize_boolean(permissions_.get('read', '')),
      'write': sanitize.sanitize_boolean(permissions_.get('write', '')),
      'is_admin': sanitize.sanitize_boolean(permissions_.get('is_admin', ''))
    }

    permission_object = UserApplications(**new_permissions)

    db.session.add(permission_object)
    db.session.commit()

    return {
      'read': permission_object.read,
      'write': permission_object.write,
      'is_admin': permission_object.is_admin
    }

  def permission_get(self, application_id, user_id):
    
    """
    Before we get the User permissions for this application, we need to make sure that
    the user requesting them is authenticated and has the `is_admin` permission for the
    application_id being requested.
    """
    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Users for Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You are not allowed to view this User\'s permissions because you are not an administrator of this Application'), 401

    permissions = UserApplications.query.filter_by(application_id=application_id,user_id=user_id).first()

    if not permissions:
      return status_.status_404('We couldn\'t find the user permissions you were looking for. This user may have been removed from the Application or the Application may have been deleted.'), 404

    return {
      'read': permissions.read,
      'write': permissions.write,
      'is_admin': permissions.is_admin
    }

  def permission_update(self, application_id, user_id, request_object):
    
    """
    Before we update the User permissions for this application, we need to make sure that
    the user requesting them is authenticated and has the `is_admin` permission for the
    application_id being requested.
    """
    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Users for Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You are not allowed to view this User\'s permissions because you are not an administrator of this Application'), 401

    permissions = UserApplications.query.filter_by(application_id=application_id,user_id=user_id).first()

    altered_permissions = json.loads(request_object.data)

    if hasattr(permissions, 'read'):
      permissions.read = sanitize.sanitize_boolean(altered_permissions.get('read', permissions.read)),

    if hasattr(permissions, 'write'):
      permissions.write = sanitize.sanitize_boolean(altered_permissions.get('write', permissions.write)),
    
    if hasattr(permissions, 'is_admin'):
      permissions.is_admin = sanitize.sanitize_boolean(altered_permissions.get('is_admin', permissions.is_admin))

    db.session.commit()

    return {
      'read': permissions.read,
      'write': permissions.write,
      'is_admin': permissions.is_admin
    }


  def permission_delete(self, application_id, user_id):
    
    """
    Before we delete the User permissions for this application, we need to make sure that
    the user requesting them is authenticated and has the `is_admin` permission for the
    application_id being requested.
    """
    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to access Users for Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You are not allowed to view this User\'s permissions because you are not an administrator of this Application'), 401

    permissions = UserApplications.query.filter_by(application_id=application_id, user_id=user_id).first()

    db.session.delete(permissions)
    db.session.commit()


"""
is_public allows us to check if feature collections are supposed to public, if
they are, then we don't need to check for OAuth crednetials to allow access
"""
class is_public(object):

    def __init__(self):
      pass

    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

          application_ = Application.query.get(kwargs['application_id'])

          keywords = kwargs

          if not is_public in keywords:
            keywords['is_public'] = False
          elif not application_.is_public:
            keywords['is_public'] = False
          else:
            keywords['is_public'] = True

          return f(*args, **keywords)
     
        return decorated_function

"""
Define our individual models
"""
class Application(db.Model, CommonsModel):

  __public__ = {'default': ['id', 'name', 'description', 'url', 'created', 'status']}

  __tablename__ = 'application'
  __table_args__ = {
    'extend_existing': True
  }

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60))
  description = db.Column(db.String(255))
  url = db.Column(db.String(255))
  created = db.Column(db.DateTime)
  status = db.Column(db.Boolean)
  is_public = db.Column(db.Boolean)
  templates = db.relationship('ApplicationTemplates', backref=db.backref('application'), cascade="all,delete")


  def __init__(self, name="", url="", description=None, created=datetime.utcnow(), status=True, is_public=True, templates=[], current_user_={}):
    self.name = name
    self.description = description
    self.url = url
    self.created = created
    self.status = status
    self.is_public = is_public
    self.templates = templates
    self.current_user = current_user_


  """
  Create a new application in the API
  """
  def application_create(self, request_object):

    """
    Make sure that some data was submitted before proceeding
    """
    if not request_object.data:
      logger.error('User %d new Application request failed because they didn\'t submit any `data` with their request', \
          self.current_user.id)
      return status_.status_400('You didn\'t include any `data` with your request.'), 400

    """
    Prepare the data for use
    """
    application_content = json.loads(request_object.data)

    """
    Make sure we have at least a name for our Application
    """
    if not application_content.get('name', ''):
      logger.error('User %d new Application request failed because the did not include a `name` in the `data`', \
          self.current_user.id)
      return status_.status_400('You didn\'t include a `name` in the `data` of your request. You have to do that with Applications.'), 400

    """
    Add the new application to the database
    """
    new_application = {
      'name': sanitize.sanitize_string(application_content.get('name', '')),
      'description': sanitize.sanitize_string(application_content.get('description', '')),
      'url': application_content.get('url', ''),
      'is_public': application_content.get('is_public', False)
    }

    application_ = Application(**new_application)

    db.session.add(application_)
    db.session.commit()

    """
    Tell the system what user should have permission to
    access the newly created application
    """
    permission = {
      'user_id': self.current_user.id,
      'application_id': application_.id,
      'read': True,
      'write': True,
      'is_admin': True
    }

    self.set_user_application_permissions(application_, permission, self.current_user)

    """
    Return the newly created Application
    """
    return application_


  """
  Get a single, existing Application from the API
  """
  def application_get(self, application_id, is_public=False):

    """
    So we'll send a request to the database for the requested applciation_id and display a Response
    to the user based on the return from the database
    """
    application = Application.query.get(application_id)

    """
    We need to check if the return from the database has return an Application
    object or a None value. If it's a None value, then we need to tell the user the application_id doesn't
    exist within the current system.
    """
    if application is None:
      return status_.status_404('The Application Requested does not exist'), 404

    """
    Check to see if the Application is_public or can be view at it's endpoint[1]
    without a bearer token.

    [1] //api.commonscloud.org/v2/applications/[ApplicationID].json 
    """
    if not is_public:

      """
      Since the Application requested is_public returned false, a bearer token
      is required to see View this application.

      This `allowed_applications` check compiles a list of `application_id` integers from the
      `user_applications` table of the database, that the user has access to 'read'
      """
      allowed_applications = self.allowed_applications('read')

      """
      If application_id requested by the user is not in the allowed_applications 'read' list
      then we need to give the user an 401 UNAUTHORIZED Response
      """
      if not application_id in allowed_applications:
        return status_.status_401('You need to be logged in to access applications'), 401

    """
    If the Application exists, go ahead and send it back to our View for formatting and display to the user
    """
    return application


  """
  Get a list of existing Applications from the API
  """
  def application_list(self):

    """
    Get a list of the applications the current user has access to
    and load their information from the database
    """
    allowed_applications = self.allowed_applications('read')

    """
    No further check is needed here because we're only return the ID's of the
    applications that we already know the user has access to. If the list is
    empty then we don't need to perform a database query and can just return
    an empty list
    """
    if len(allowed_applications) >= 1:
      return Application.query.filter(Application.id.in_(allowed_applications)).all()

    return []


  """
  Create a new application in the CommonsCloudAPI

  @param (object) self

  @param (dictionary) application_content
      The content that is being submitted by the user
  """
  def application_update(self, application_id, request_object):

    allowed_applications = self.allowed_applications('write')
    
    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to update Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You need to be logged in to access applications'), 401

    application_ = Application.query.get(application_id)

    application_content = json.loads(request_object.data)

    """
    Part 2: Update the fields that we have data for
    """
    if hasattr(application_, 'name'):
      application_.name = sanitize.sanitize_string(application_content.get('name', application_.name))

    if hasattr(application_, 'description'):
      application_.description = sanitize.sanitize_string(application_content.get('description', application_.description))

    if hasattr(application_, 'url'):
      application_.url = sanitize.sanitize_string(application_content.get('url', application_.url))

    db.session.commit()

    return application_


  """
  Get an existing Applications from the CommonsCloudAPI

  @param (object) self

  @param (int) application_id
      The unique ID of the Application to be retrieved from the system

  @return (object) application_
      A fully qualified Application object

  """
  def application_delete(self, application_id):

    allowed_applications = self.allowed_applications('is_admin')

    if not application_id in allowed_applications:
      logger.warning('User %d with Applications %s tried to delete Application %d', \
          self.current_user.id, allowed_applications, application_id)
      return status_.status_401('You need to be logged in to access applications'), 401

    application_ = Application.query.get(application_id)

    db.session.delete(application_)
    db.session.commit()


  """
  Associate a user with a specific application

  @param (object) self

  @param (object) application
      A fully qualified Application object to act on

  @param (dict) permission
      A dictionary containing boolean values for the `read`, `write`, and `is_admin` properties

      Example: 

        permission = {
          'read': True,
          'write': True,
          'is_admin': True
        }

  @param (object) user
      A fully qualified User object that we can act on

  @return (object) new_permission
      The permission object that was saved to the database

  """
  def set_user_application_permissions(self, application, permission, user):

    """
    Start a new Permission object
    """
    new_permission = UserApplications(**permission)

    """
    Set the ID of the Application to act upon
    """
    new_permission.application_id = application.id

    """
    Add the new permissions defined with the user defined
    """
    user.applications.append(new_permission)
    db.session.commit()

    return new_permission
