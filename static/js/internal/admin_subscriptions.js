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
    $scope.currentCategories = function() {
        if (!$scope.categories) {
            return [];
        }
        var current = [];
        var i;
        var inArray;
        for (i = 0; i < $scope.categories.length; i++) {
            inArray = $scope.gallery.gallery_categories.filter(function(obj) {
                return obj.category_uuid == $scope.categories[i].uuid;
            });
            if (inArray.length == 0) {
                current.push($scope.categories[i]);
            }
            inArray = [];
        }
        return current;
    };
    $scope.addCategory = function(subscription) {
        $http.post('/admin/api//' + $scope.gallery_uuid + '/categories', data={'category_uuid': category.uuid}).success(function(response) {
            $scope.gallery.gallery_categories = response;
            $scope.newCategory = '';
        });
    };
    $scope.removeCategory = function(category) {
        $http.delete('/admin/api/gallery/' + $scope.gallery_uuid + '/categories/' + category.uuid).success(function(response) {
            $scope.gallery.gallery_categories = response;
            $scope.newCategory = '';
        });
    };
}]);
