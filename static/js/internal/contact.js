angularApp.controller('ContactController', ['$scope', '$http', '$log', function($scope, $http, $log) {
  $scope.fromEmail = '';
  $scope.subject = '';
  $scope.body = '';
  $scope.sendEmail = function() {
    if (!$scope.fromEmail || !$scope.body) {
      $scope.toggleAlert(true, 'alert-info', 'Emails require a from email and body.');
      return;
    }
    var data = {'email': $scope.fromEmail,
                'subject': $scope.subject,
                'body': $scope.body}
    $http.post("/send/email", data).success(function(data) {
      $scope.fromEmail = '';
      $scope.subject = '';
      $scope.body = '';
      $scope.toggleAlert(true, 'alert-success', 'Your email was successfully sent.');
    }).error(function(data) {
      $scope.toggleAlert(true, 'alert-danger', 'There was an error sending your email. My bad. You can email me directly at kate@heddleston.com to complain. Thanks!');
    });
  };
  $scope.toggleAlert = function(show, showClass, message) {
    var al = $('.contact-page .alert');
    al.find('.message').html('');
    al.removeClass('alert-success alert-warning alert-danger alert-info').hide();
    if (show) {
      al.find('.message').html(message);
      al.addClass(showClass).show();
    }
  };
}]);
