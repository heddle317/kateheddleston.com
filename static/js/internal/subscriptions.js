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
