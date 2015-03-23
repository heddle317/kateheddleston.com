angularApp.controller('AdminSubscriptionController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.subscriptions = [];
    $scope.currentSubscriber = null;
    $http.get('/admin/api/subscriptions').success(function(response) {
        $scope.subscriptions = response;
        $scope.activeSubscribers = [];
        $scope.unverifiedSubscribers = [];
        $scope.unsubscribed = [];
        var s;
        for (var i = 0; i < $scope.subscriptions.length; i++) {
            s = $scope.subscriptions[i];
            if (s.dead) {
                $scope.unsubscribed.push(s);
            } else if(s.verified) {
                $scope.activeSubscribers.push(s);
            } else {
                $scope.unverifiedSubscribers.push(s);
            }
        }
    });
    $scope.sendVerificationEmail = function(subscription) {
        var confirm = $window.confirm("Are you sure you want to resend " + subscription.email +"'s verification email?");
        if (!confirm) {
            return;
        }
        var $btn = $('.' + subscription.uuid + ' .btn.verify').button('loading');
        $http.post('/admin/api/subscriptions/' + subscription.uuid + '/verify').success(function(response) {
            $('.' + subscription.uuid + ' .fa-check').show('fast').delay(3000).fadeOut(300);
        }).finally(function() {
            $btn.button('reset');
        });
    };
    $http.get('/admin/api/categories').success(function(response) {
        $scope.categories = response;
    });
    $scope.toggleCategory = function(subscription, category) {
        if ($scope.hasCategory(subscription, category) >= 0) {
            $scope.removeCategory(subscription, category);
        } else {
            $scope.addCategory(subscription, category);
        }
    };
    $scope.hasCategory = function(subscription, category) {
        var i;
        for (i = 0; i < subscription.categories.length; i++) {
            if (subscription.categories[i].category_uuid == category.uuid) {
                return i;
            }
        }
        return -1;
    }
    $scope.addCategory = function(subscription, category) {
        $http.post('/admin/api/subscriptions/' + subscription.uuid + '/categories', data={'category_uuid': category.uuid}).success(function(response) {
            var index = $scope.subscriptions.indexOf(subscription);
            $scope.subscriptions[index] = response;
        });
    };
    $scope.removeCategory = function(subscription, category) {
        $http.delete('/admin/api/subscriptions/' + subscription.uuid + '/categories/' + category.uuid).success(function(response) {
            var index = $scope.subscriptions.indexOf(subscription);
            $scope.subscriptions[index] = response;
        });
    };
}]);
