angularApp.controller('AdminUsersController', ['$scope', '$http', '$window', '$log', function($scope, $http, $window, $log) {
    $scope.users = [];
    $scope.currentSubscriber = null;
    $scope.email = '';
    $http.get('/admin/api/users').success(function(response) {
        $scope.users = response;
    });
    $scope.sendInviteEmail = function() {
        var confirm = $window.confirm("Are you sure you want to send an invitation to " + $scope.email +"?");
        if (!confirm) {
            return;
        }
        var $btn = $('.send-invite').button('loading');
        $http.post('/admin/api/users/invite', data={'email': $scope.email}).success(function(response) {
            $scope.email = '';
        }).finally(function() {
            $btn.button('reset');
        });
    };
}]);
