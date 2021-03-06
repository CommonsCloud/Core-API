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
from flask import request
from flask import send_from_directory


"""
Import Application Dependencies
"""
from CommonsCloudAPI.extensions import oauth
from CommonsCloudAPI.extensions import logger
from CommonsCloudAPI.extensions import status as status_

from CommonsCloudAPI.models.feature import Feature
from CommonsCloudAPI.models.feature import is_public
from CommonsCloudAPI.models.feature import is_crowdsourced

from . import module


@module.route('/v2/type_<string:storage>.<string:extension>', methods=['OPTIONS'])
def features_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/func.<string:extension>', methods=['OPTIONS'])
def features_func_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['OPTIONS'])
def features_single_preflight(storage, feature_id, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/type_<string:relationship>.<string:extension>', methods=['OPTIONS'])
def features_relationship_preflight(storage, feature_id, relationship, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/attachment_<string:relationship>.<string:extension>', methods=['OPTIONS'])
def features_attachment_preflight(storage, feature_id, relationship, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/intersects.<string:extension>', methods=['OPTIONS'])
def features_intersects_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/region.<string:extension>', methods=['OPTIONS'])
def features_region_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/attachment_<string:attachment_storage>/<int:attachment_id>.<string:extension>', methods=['OPTIONS'])
def attachment_delete_preflight(storage, feature_id, attachment_storage, attachment_id, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/import.<string:extension>', methods=['OPTIONS'])
def features_import_preflight(storage, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/users.<string:extension>', methods=['OPTIONS'])
def features_users_preflight(storage, feature_id, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>/<int:feature_id>/users/<int:user_id>.<string:extension>', methods=['OPTIONS'])
def features_users_single_preflight(storage, feature_id, user_id, extension):
    return status_.status_200(), 200

@module.route('/v2/type_<string:storage>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_list(oauth_request, storage, extension, is_public):

    # if (extension == 'csv'):
    #     return status_.status_415('We do not support exporting a feature list as a CSV file yet, but we\'re working on it.'), 415
    if (extension == 'shp'):
        return status_.status_415('We do not support exporting a feature list as a SHP file yet, but we\'re working on it.'), 415

    results_per_page = request.args.get('results_per_page')
    if not results_per_page:
        results_per_page = 25
    else:
        results_per_page = int(request.args.get('results_per_page'))

    if 'false' == request.args.get('statistics'):
        show_statistics = False
    else:
        show_statistics = True

    if 'false' == request.args.get('relationship'):
        show_relationship = False
    else:
        show_relationship = True

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_list(storage, results_per_page, show_statistics, show_relationship)

    if type(feature_list) is tuple:
        return feature_list

    feature_results = feature_list.get('results')
    features_last_modified = Feature_.features_last_modified(feature_list.get('model'))

    """
    Get Statistics for this Feature set if they are requested by setting statistics to True
    """
    feature_statistics = None
    if show_statistics:
        feature_statistics = Feature_.feature_statistic(feature_list.get('model'),feature_list.get('template'))

    arguments = {
        'the_content': feature_results.get('objects'),
        'list_name': 'features',
        'extension': extension,
        'current_page': feature_results.get('page'),
        'total_pages': feature_results.get('total_pages'),
        'total_features': feature_results.get('num_results'),
        'features_per_page': results_per_page,
        'statistics': feature_statistics,
        'last_modified': features_last_modified
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/func.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_func(oauth_request, storage, extension, is_public):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    function_return = Feature_.feature_evaluate_function(storage)

    if type(function_return) is tuple:
        return function_return

    arguments = {
        'the_content': function_return,
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get(oauth_request, storage, feature_id, extension, is_public):

    if (extension == 'csv'):
        return status_.status_415('We do not support exporting a single item as a CSV file.'), 415

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature = Feature_.feature_get(storage, feature_id)

    if type(feature) is tuple:
        return feature

    arguments = {
        'the_content': feature,
        "extension": extension,
        'code': 200
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/<int:feature_id>/attachment_<string:relationship>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get_attachment_relationship(oauth_request, storage, feature_id, relationship, extension, is_public):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature = Feature_.feature_get_attachment_relationship(storage, feature_id, relationship)

    if type(feature) is tuple:
        return feature

    arguments = {
        "the_content": feature,
        "list_name": "features",
        "extension": extension,
        "code": 200
    }

    if (extension == 'csv'):
        return status_.status_415("We do not support exporting a single item or it's relationships as a CSV file."), 415

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>/type_<string:relationship>.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get_relationship(oauth_request, storage, feature_id, relationship, extension, is_public):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature = Feature_.feature_get_relationship(storage, feature_id, relationship)

    if type(feature) is tuple:
        return feature

    arguments = {
        "the_content": feature,
        "list_name": "features",
        "extension": extension,
        "code": 200
    }

    if (extension == 'csv'):
        return status_.status_415("We do not support exporting a single item or it's relationships as a CSV file."), 415

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>.<string:extension>', methods=['POST'])
@is_crowdsourced()
@oauth.oauth_or_crowdsourced()
def feature_create(oauth_request, storage, extension, is_crowdsourced):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    new_feature = Feature_.feature_create(request, storage)

    if type(new_feature) is tuple:
        return new_feature

    try:
        return status_.status_201(new_feature.id), 201
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['PATCH','PUT'])
@oauth.require_oauth()
def feature_update(oauth_request, storage, feature_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    updated_feature = Feature_.feature_update(request, storage, feature_id)

    if type(updated_feature) is tuple:
        return updated_feature

    arguments = {
      "the_content": updated_feature,
      "extension": extension
    }

    try:
        return Feature_.endpoint_response(**arguments)
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def feature_delete(oauth_request, storage, feature_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    deleted_feature = Feature_.feature_delete(storage, feature_id)

    if type(deleted_feature) is tuple:
        return deleted_feature

    try:
        return status_.status_204(), 204
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/<int:feature_id>/attachment_<string:attachment_storage>/<int:attachment_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def attachment_delete(oauth_request, storage, feature_id, attachment_storage, attachment_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    Feature_.attachment_delete(storage, feature_id, 'attachment_' + attachment_storage, attachment_id)

    try:
        return status_.status_204(), 204
    except Exception as e:
        return status_.status_500(e), 500


@module.route('/v2/type_<string:storage>/intersects.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_intersects(oauth_request, storage, extension, is_public):

    geometry = request.args.get('geometry')
    results_per_page = request.args.get('results_per_page')

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_get_intersection(storage, geometry)

    if type(feature_list) is tuple:
        return feature_list

    arguments = {
        'the_content': feature_list,
        'list_name': 'features',
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/region.<string:extension>', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_region(oauth_request, storage, extension, is_public):

    geometry = request.args.get('geometry')
    results_per_page = request.args.get('results_per_page')

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_list = Feature_.feature_get_content_for_region(storage, geometry)

    if type(feature_list) is tuple:
        return feature_list

    arguments = {
        'the_content': feature_list,
        'list_name': 'features',
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)


@module.route('/v2/type_<string:storage>/excel-template', methods=['GET'])
@is_public()
@oauth.oauth_or_public()
def feature_get_excel_template(oauth_request, storage, is_public):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    excel_template = Feature_.feature_get_excel_template(storage)

    logger.warning('excel_template %s', excel_template)

    # return status_.status_200(), 200

    return send_from_directory(excel_template.get('directory'), excel_template.get('filename'), as_attachment=True)


@module.route('/v2/type_<string:storage>/import.<string:extension>', methods=['POST'])
@oauth.require_oauth()
def feature_import(oauth_request, storage, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    import_features = Feature_.feature_import(request, storage)

    return status_.status_200(), 200


@module.route('/v2/type_<string:storage>/batch.<string:extension>', methods=['POST'])
# @oauth.require_oauth()
def feature_batch(storage, extension):

    Feature_ = Feature()
    # Feature_.current_user = oauth_request.user
    import_features = Feature_.feature_batch(request, storage)

    if type(import_features) is tuple:
        return import_features

    return status_.status_200(), 200


@module.route('/v2/type_<string:storage>/<int:feature_id>/users.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def features_users(oauth_request, storage, feature_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    feature_user_list = Feature_.feature_users(storage, feature_id)

    if type(feature_user_list) is tuple:
        return feature_user_list

    arguments = {
        'the_content': feature_user_list,
        'list_name': 'users',
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>/users/<int:user_id>.<string:extension>', methods=['GET'])
@oauth.require_oauth()
def features_users_get(oauth_request, storage, feature_id, user_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    user_permissions = Feature_.permission_get(storage, feature_id, user_id)

    if type(user_permissions) is tuple:
        return user_permissions

    arguments = {
        'the_content': user_permissions,
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>/users/<int:user_id>.<string:extension>', methods=['POST'])
@oauth.require_oauth()
def features_users_create(oauth_request, storage, feature_id, user_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    user_permissions = Feature_.permission_create(storage, feature_id, user_id, request)

    if type(user_permissions) is tuple:
        return user_permissions

    arguments = {
        'the_content': user_permissions,
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>/users/<int:user_id>.<string:extension>', methods=['PUT', 'PATCH'])
@oauth.require_oauth()
def features_users_update(oauth_request, storage, feature_id, user_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    user_permissions = Feature_.permission_update(storage, feature_id, user_id, request)

    if type(user_permissions) is tuple:
        return user_permissions

    arguments = {
        'the_content': user_permissions,
        'extension': extension
    }

    return Feature_.endpoint_response(**arguments)

@module.route('/v2/type_<string:storage>/<int:feature_id>/users/<int:user_id>.<string:extension>', methods=['DELETE'])
@oauth.require_oauth()
def features_users_delete(oauth_request, storage, feature_id, user_id, extension):

    Feature_ = Feature()
    Feature_.current_user = oauth_request.user
    user_permissions = Feature_.permission_delete(storage, feature_id, user_id)

    if type(user_permissions) is tuple:
        return user_permissions

    return status_.status_204(), 204