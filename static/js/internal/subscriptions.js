angularApp.controller('SubscriptionController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.name = '';
    $scope.email = '';
    $scope.message = '';
    $scope.error = false;
    $scope.success = false;
    $scope.close = function() {
        $scope.name = '';
        $scope.email = '';
        $scope.message = '';
        $scope.error = false;
        $scope.success = false;
        $scope.loading = false;
        $('#subscribe').modal('hide');
    };
    $scope.subscribe = function() {
        $scope.error = 'false';
        $scope.message = '';
        if (!$scope.name || !$scope.email) {
            $scope.error = true;
            $scope.message = 'Name and email address are required.';
            return;
        }
        $scope.loading = true;
        data = {'name': $scope.name,
                'email': $scope.email}
        $http.post('/subscriptions/subscribe', data).success(function(data, status, headers, config) {
            $scope.success = true;
            $scope.message = data.message;
        }).error(function(data, status, headers, config) {
            $scope.error = true;
            $scope.message = data.message;
        }).then(function() {
            $scope.loading = false;
        });
    };
}]);


angularApp.controller('EditSubscriptionController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.subscription = null;
    $scope.categories = [];
    $http.get('/subscription/categories').success(function(response) {
        $scope.categories = response;
    });
    $scope.initSubscription = function(subscription) {
        $scope.subscription = angular.fromJson(subscription);
    };
    $scope.resubscribe = function() {
        var $btn = $('.resubscribe').button('loading');
        $http.post('/subscription/' + $scope.subscription.uuid, data={'dead': false}).success(function(response) {
            $scope.subscription = response;
            $scope.success = true;
        }).error(function(response) {
            $scope.error = true;
            $scope.message = data.message;
        }).then(function() {
            $btn.button('reset');
        });
    };
    $scope.cancelSubscription = function() {
        var confirm = $window.confirm("Are you sure you want to cancel your subscription? You will no longer receive any notifications from this blog.");
        if (!confirm) {
            return;
        }
        var $btn = $('.cancel-subscription').button('loading');
        $http.delete('/subscription/' + $scope.subscription.uuid).success(function(response, status, headers, config) {
            $scope.subscription = response;
            $scope.success = true;
        }).error(function(response) {
            $scope.error = true;
            $scope.message = data.message;
        }).then(function() {
            $btn.button('reset');
        });
    };
    $scope.addCategory = function(category) {
        $('.' + category.uuid + ' .loading').show();
        $http.post('/subscription/' + $scope.subscription.uuid + '/categories', data={'category_uuid': category.uuid}).success(function(response) {
            $scope.subscription = response;
            var elem = $('.' + category.uuid + ' .fa-thumbs-up').show();
            setTimeout(function(){ elem.fadeOut() }, 1000);
        }).error(function(response) {
            var elem = $('.' + category.uuid + ' .fa-close').show();
            setTimeout(function(){ elem.fadeOut() }, 1000);
        }).then(function() {
            $('.' + category.uuid + ' .loading').hide();
        });
    };
    $scope.removeCategory = function(category) {
        $('.' + category.uuid + ' .loading').show();
        $http.delete('/subscription/' + $scope.subscription.uuid + '/categories/' + category.uuid).success(function(response) {
            $scope.subscription = response;
            var elem = $('.' + category.uuid + ' .fa-frown-o').show();
            setTimeout(function(){ elem.fadeOut() }, 1000);
        }).error(function(response) {
            var elem = $('.' + category.uuid + ' .fa-close').show();
            setTimeout(function(){ elem.fadeOut() }, 1000);
        }).then(function() {
            $('.' + category.uuid + ' .loading').hide();
            if ($scope.subscription.categories.length == 0) {
                $scope.cancelSubscription();
            }
        });
    };
    $scope.toggleCategory = function(category) {
        if ($scope.hasCategory(category) >= 0) {
            $scope.removeCategory(category);
        } else {
            $scope.addCategory(category);
        }
    };
    $scope.hasCategory = function(category) {
        var i;
        for (i = 0; i < $scope.subscription.categories.length; i++) {
            if ($scope.subscription.categories[i].category_uuid == category.uuid) {
                return i;
            }
        }
        return -1;
    };
}]);
