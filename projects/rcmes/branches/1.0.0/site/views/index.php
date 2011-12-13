<?php
$app = $GLOBALS['app'];
$wrmDatabase = $app->getDataProvider('MySqlDataProvider');
$wrmDatabase->connect(
	array("server"     => $app->settings['wrm_server'],
          "username"   => $app->settings['wrm_user'],
          "password"   => $app->settings['wrm_pass'],
          "database"   => $app->settings['wrm_database']));

$sqlDatasetCount   = "SELECT count(*) as dsCount    FROM `dataset` ";
$sqlParameterCount = "SELECT count(*) as paramCount FROM `parameter` ";
$sqlDataPointCount = "SELECT count(*) as dpCount    FROM `dataPoint` ";

$response   = $wrmDatabase->request($sqlDatasetCount,array("format"=>"assoc"));
$dsCount    = $response->data[0]['dsCount'];
$response   = $wrmDatabase->request($sqlParameterCount,array("format"=>"assoc"));
$paramCount = $response->data[0]['paramCount'];
$response   = $wrmDatabase->request($sqlDataPointCount,array("format"=>"assoc"));
$dpCount    = $response->data[0]['dpCount'];

// Format the data point count so that it is concise
$labels = array("K","M","B","T");
$counts = array(1000,1000000,1000000000,1000000000000);
$temp   = 0;
for ($i = 0; $i < count($labels); $i++) {
	$temp = $dpCount / $counts[$i];
	if ($temp < 1000) {
		$dpCount = round($temp,1);
		$dpLabel = $labels[$i];
		break;
	}
}

?>
<script type="text/javascript">
	$(document).ready(function() {
		$.get('<?php echo SITE_ROOT?>/newsfeeds/channel.do',
			{"channel" : "news" },
			function(data) {
				$('#newsfeed').html(data);
				$('.nf_author').addClass('quiet').prepend('Posted by: ');
		});
		

	});
	
	$(document).ready(function() {
	   $.get('<?php echo SITE_ROOT?>/prodrss/rss.do', 
	      {"channel" : "ALL",
		   "perPage" : 10},
	      function(data){
	         $('#prods').html(data);
	      }
	   );
	});
</script>
<div class="span-20 push-3 last" id="stats">
	<h2 class="larger loud">The Database at a Glance...</h2>
	<div class="span-5 colborder stat">
		<h3>Datasets</h3>
		<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg"/>
		<div class="number"><?php echo $dsCount?></div>
		<a href="<?php echo SITE_ROOT?>/datasets/">See All Datasets</a>
	</div>
	<div class="span-5 colborder stat">
		<h3>Parameters</h3>
		<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg"/>
		<div class="number"><?php echo $paramCount?></div>
		<a href="<?php echo SITE_ROOT?>/parameters">Browse Parameters</a>
	</div>
	<div class="span-5 last stat">
		<h3>Data Points</h3>
		<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg"/>
		<div class="number"><?php echo $dpCount . $dpLabel?></div>
		<a href="<?php echo SITE_ROOT?>/browse/">Search for Data</a>
	</div>
</div>
<hr class="space"/>
<hr/>
	<div class="span-10 colborder">
		<h2>Latest News...</h2>
		<div id="newsfeed">
			<span class="quiet">Latest News Loading...</span>
		</div>
		
	</div>
	<div class="span-7 colborder">
	    <h2>Latest Data Products...</h2>
	    <br/>
	    <div id="prods">
	       <span class="quiet">Latest Products Loading...</span>
	    </div>
	</div>