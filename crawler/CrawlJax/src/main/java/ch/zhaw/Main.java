package ch.zhaw;

import com.crawljax.browser.EmbeddedBrowser;
import com.crawljax.browser.EmbeddedBrowser.BrowserType;
import com.crawljax.browser.WebDriverBrowserBuilder;
import com.crawljax.core.CrawljaxRunner;
import com.crawljax.core.configuration.BrowserConfiguration;
import com.crawljax.core.configuration.BrowserOptions;
import com.crawljax.core.configuration.CrawlRules.FormFillMode;
import com.crawljax.core.configuration.CrawljaxConfiguration;
import com.crawljax.core.configuration.CrawljaxConfiguration.CrawljaxConfigurationBuilder;
import com.crawljax.core.configuration.ProxyConfiguration;
import com.crawljax.stateabstractions.visual.imagehashes.DHashStateVertexFactory;
import org.openqa.selenium.Platform;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

/**
 * Example of running Crawljax with the CrawlOverview plugin on a single-page web app. The crawl
 * will produce output using the {@link CrawlOverview} plugin. Default output dir is "out".
 */
public final class Main {

    private static final long WAIT_TIME_AFTER_EVENT = 200;
    private static final long WAIT_TIME_AFTER_RELOAD = 200;
    private static final String URL = "http://0.0.0.0:8085/";

    /**
     * Run this method to start the crawl.
     *
     * @throws IOException when the output folder cannot be created or emptied.
     */
    public static void main(String[] args) throws IOException {

        CrawljaxConfigurationBuilder builder = CrawljaxConfiguration.builderFor(args[0]);

        int proxy_port = 8080;

        if(args.length == 2) {
            proxy_port = Integer.parseInt(args[1]);
        }

        builder.crawlRules().setFormFillMode(FormFillMode.NORMAL);

        // click these elements
        builder.crawlRules().clickDefaultElements();

        //builder.crawlRules().dontClickChildrenOf(".user-info");
        /*builder.crawlRules().click("A");
        builder.crawlRules().click("button");*/
        builder.crawlRules().crawlHiddenAnchors(true);
        builder.crawlRules().crawlFrames(false);
        builder.setUnlimitedRuntime();
        //builder.setUnlimitedStates();
        builder.setStateVertexFactory(new DHashStateVertexFactory());

        // builder.setMaximumStates(10);
         //builder.setMaximumDepth(5);
        builder.setUnlimitedCrawlDepth();
        builder.crawlRules().clickElementsInRandomOrder(false);
        // Set timeouts
        builder.crawlRules().waitAfterReloadUrl(WAIT_TIME_AFTER_RELOAD, TimeUnit.MILLISECONDS);
        builder.crawlRules().waitAfterEvent(WAIT_TIME_AFTER_EVENT, TimeUnit.MILLISECONDS);
        builder.setBrowserConfig(new BrowserConfiguration(BrowserType.CHROME, 1));
        //builder.setBrowserConfig(BrowserConfiguration.remoteConfig(1, "http://localhost:9515", new DesiredCapabilities()));
        builder.setProxyConfig(ProxyConfiguration.manualProxyOn("0.0.0.0", proxy_port));
        //builder.addPlugin(new CrawlOverview());

        // CrawlOverview
        //builder.addPlugin(new CrawlOverview());

        CrawljaxRunner crawljax = new CrawljaxRunner(builder.build());
        crawljax.call();
    }
}