CREATE TABLE `cake` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL DEFAULT '' COMMENT '蛋糕名字',
  `price` float(20,3) NOT NULL DEFAULT '0.000' COMMENT '价格, 其实应该是用descimal或者int的',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='下次去蹭Seven家得蛋糕';
