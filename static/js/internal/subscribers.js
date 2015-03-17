angularApp.controller('SubscriptionController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.subscribers = [];
    $scope.currentSubscriber = null;
    $http.get('/admin/api/subscribers').success(function(response) {
        $scope.subscribers = response;
        $scope.activeSubscribers = [];
        $scope.unverifiedSubscribers = [];
        $scope.unsubscribed = [];
        var s;
        for (var i = 0; i < $scope.subscribers.length; i++) {
            s = $scope.subscribers[i];
            if (s.dead) {
                $scope.unsubscribed.push(s);
            } else if(s.verified) {
                $scope.activeSubscribers.push(s);
            } else {
                $scope.unverifiedSubscribers.push(s);
            }
        }
    });
    $scope.sendVerificationEmail = function(subscriber) {
        var confirm = $window.confirm("Are you sure you want to resend " + subscriber.email +"'s verification email?");
        if (!confirm) {
            return;
        }
        var $btn = $('.' + subscriber.uuid + ' .btn.verify').button('loading');
        $http.post('/admin/api/subscribers/' + subscriber.uuid + '/verify').success(function(response) {
            $('.' + subscriber.uuid + ' .fa-check').show('fast').delay(3000).fadeOut(300);
        }).finally(function() {
            $btn.button('reset');
        });
    };
}]);
