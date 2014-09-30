$(document).ready(function() {
  $('#comment-tooltip').popover({html: true,
                                 viewport: {'selector': 'body', 'padding': 20}});
});

function CommentCtrl($scope, $http, $log) {
  $scope.tooltipContent = "I use Twitter for comments because Twitter is largely a public forum. I don't want comment threads on my website to be a place where people can hide behind anonymity and make cruel remarks. I appreciate all thoughtful, funny, and constructive comments opinions about the content posted here. If you are not comfortable using Twitter to voice your thoughts then you may reach out to me directly.<br><br><strong>Why do I add the blog post link to the tweet?</strong><br>To shamelessly promote my content of course. Actually, the link is how I find the tweets through Twitter's API to display here."
};
