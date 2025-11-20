#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAIR Monte Carlo Simulation Tool
Based on Factor Analysis of Information Risk (FAIR) methodology

Risk = Loss Event Frequency (LEF) × Loss Magnitude (LM)
LEF = Threat Event Frequency (TEF) × Vulnerability (Vuln)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json


@dataclass
class FAIRDistribution:
    """Represents a probability distribution for FAIR parameters"""
    dist_type: str  # 'pert', 'lognormal', 'uniform', 'triangular'
    min_val: float
    mode_val: float = None
    max_val: float = None
    mean: float = None
    std: float = None
    
    def sample(self, size: int) -> np.ndarray:
        """Generate random samples from the distribution"""
        if self.dist_type == 'pert':
            # PERT distribution (Beta PERT)
            # Lambda parameter controls the shape (typically 4)
            lambda_param = 4
            mu = (self.min_val + lambda_param * self.mode_val + self.max_val) / (lambda_param + 2)
            
            if self.max_val == self.min_val:
                return np.full(size, self.min_val)
            
            # Shape parameters for Beta distribution
            alpha = 1 + lambda_param * (self.mode_val - self.min_val) / (self.max_val - self.min_val)
            beta = 1 + lambda_param * (self.max_val - self.mode_val) / (self.max_val - self.min_val)
            
            # Generate Beta distribution samples and scale to range
            beta_samples = np.random.beta(alpha, beta, size)
            return self.min_val + beta_samples * (self.max_val - self.min_val)
            
        elif self.dist_type == 'lognormal':
            # Lognormal distribution (good for loss magnitudes)
            if self.mean is not None and self.std is not None:
                # Calculate lognormal parameters from mean and std
                variance = self.std ** 2
                mu = np.log(self.mean ** 2 / np.sqrt(variance + self.mean ** 2))
                sigma = np.sqrt(np.log(1 + variance / (self.mean ** 2)))
                return np.random.lognormal(mu, sigma, size)
            else:
                # Use min and max to estimate parameters
                mu = np.log(self.mode_val)
                sigma = (np.log(self.max_val) - np.log(self.min_val)) / 4
                return np.random.lognormal(mu, sigma, size)
                
        elif self.dist_type == 'uniform':
            return np.random.uniform(self.min_val, self.max_val, size)
            
        elif self.dist_type == 'triangular':
            return np.random.triangular(self.min_val, self.mode_val, self.max_val, size)
        
        else:
            raise ValueError(f"Unknown distribution type: {self.dist_type}")


class FAIRMonteCarloSimulation:
    """FAIR-based Monte Carlo simulation engine"""
    
    def __init__(self, n_simulations: int = 10000):
        self.n_simulations = n_simulations
        self.results = None
        
    def run_simulation(self, 
                      tef_dist: FAIRDistribution,
                      vuln_prob: float,
                      primary_loss_dist: FAIRDistribution,
                      secondary_loss_dist: FAIRDistribution = None,
                      secondary_loss_prob: float = 0.0) -> Dict:
        """
        Run FAIR Monte Carlo simulation
        
        Parameters:
        -----------
        tef_dist: Distribution for Threat Event Frequency (events per year)
        vuln_prob: Probability of vulnerability (0-1) - Contact Frequency × Probability of Action × Vulnerability
        primary_loss_dist: Distribution for Primary Loss Magnitude (€)
        secondary_loss_dist: Distribution for Secondary Loss Magnitude (€)
        secondary_loss_prob: Probability that secondary losses occur (0-1)
        
        Returns:
        --------
        Dictionary with simulation results and statistics
        """
        
        # Sample Threat Event Frequency
        tef_samples = tef_dist.sample(self.n_simulations)
        
        # Calculate Loss Event Frequency
        # LEF = TEF × Vulnerability
        lef_samples = tef_samples * vuln_prob
        
        # For each simulation, determine actual number of loss events
        # Using Poisson distribution based on the expected frequency
        actual_events = np.random.poisson(lef_samples)
        
        # Calculate losses for each simulation
        annual_losses = np.zeros(self.n_simulations)
        
        for i in range(self.n_simulations):
            if actual_events[i] > 0:
                # Sample primary losses for each event
                primary_losses = primary_loss_dist.sample(actual_events[i])
                
                # Sample secondary losses if applicable
                if secondary_loss_dist is not None and secondary_loss_prob > 0:
                    # Determine which events have secondary losses
                    has_secondary = np.random.random(actual_events[i]) < secondary_loss_prob
                    secondary_losses = np.where(
                        has_secondary,
                        secondary_loss_dist.sample(actual_events[i]),
                        0
                    )
                else:
                    secondary_losses = 0
                
                # Total annual loss for this simulation
                annual_losses[i] = np.sum(primary_losses) + np.sum(secondary_losses)
        
        # Store results
        self.results = {
            'annual_losses': annual_losses,
            'lef_samples': lef_samples,
            'actual_events': actual_events,
            'tef_samples': tef_samples
        }
        
        # Calculate statistics
        stats_dict = self._calculate_statistics(annual_losses, lef_samples)
        
        return stats_dict
    
    def _calculate_statistics(self, annual_losses: np.ndarray, lef_samples: np.ndarray) -> Dict:
        """Calculate key statistics from simulation results"""
        
        # Remove zeros for non-zero statistics
        non_zero_losses = annual_losses[annual_losses > 0]
        
        stats = {
            'ale_mean': np.mean(annual_losses),
            'ale_median': np.median(annual_losses),
            'ale_std': np.std(annual_losses),
            'ale_min': np.min(annual_losses),
            'ale_max': np.max(annual_losses),
            'percentiles': {
                '10th': np.percentile(annual_losses, 10),
                '25th': np.percentile(annual_losses, 25),
                '50th': np.percentile(annual_losses, 50),
                '75th': np.percentile(annual_losses, 75),
                '90th': np.percentile(annual_losses, 90),
                '95th': np.percentile(annual_losses, 95),
                '99th': np.percentile(annual_losses, 99)
            },
            'lef_mean': np.mean(lef_samples),
            'lef_median': np.median(lef_samples),
            'probability_of_loss': len(non_zero_losses) / len(annual_losses),
            'mean_loss_given_event': np.mean(non_zero_losses) if len(non_zero_losses) > 0 else 0
        }
        
        return stats
    
    def print_results(self, stats: Dict, currency: str = "€"):
        """Print formatted simulation results"""
        print("\n" + "="*60)
        print("FAIR MONTE CARLO SIMULATION RESULTS")
        print("="*60)
        print(f"\nNumber of simulations: {self.n_simulations:,}")
        
        print(f"\n📊 ANNUAL LOSS EXPECTANCY (ALE)")
        print(f"Mean ALE:          {currency}{stats['ale_mean']:,.2f}")
        print(f"Median ALE:        {currency}{stats['ale_median']:,.2f}")
        print(f"Std Deviation:     {currency}{stats['ale_std']:,.2f}")
        
        print(f"\n📈 PERCENTILES")
        for pct, val in stats['percentiles'].items():
            print(f"{pct:>5} percentile:  {currency}{val:,.2f}")
        
        print(f"\n🎯 LOSS EVENT FREQUENCY")
        print(f"Mean LEF:          {stats['lef_mean']:.4f} events/year")
        print(f"Median LEF:        {stats['lef_median']:.4f} events/year")
        
        print(f"\n💡 KEY INSIGHTS")
        print(f"Probability of at least one loss event: {stats['probability_of_loss']*100:.1f}%")
        if stats['mean_loss_given_event'] > 0:
            print(f"Mean loss given an event occurs:        {currency}{stats['mean_loss_given_event']:,.2f}")
        
        print("\n" + "="*60 + "\n")
    
    def plot_results(self, stats: Dict, currency: str = "€", save_path: str = None):
        """Generate visualization of simulation results"""
        if self.results is None:
            raise ValueError("No simulation results available. Run simulation first.")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('FAIR Monte Carlo Simulation Results', fontsize=16, fontweight='bold')
        
        annual_losses = self.results['annual_losses']
        lef_samples = self.results['lef_samples']
        
        # 1. Annual Loss Distribution (Histogram)
        ax1 = axes[0, 0]
        ax1.hist(annual_losses, bins=50, edgecolor='black', alpha=0.7, color='#2E86AB')
        ax1.axvline(stats['ale_mean'], color='red', linestyle='--', linewidth=2, label=f'Mean: {currency}{stats["ale_mean"]:,.0f}')
        ax1.axvline(stats['ale_median'], color='orange', linestyle='--', linewidth=2, label=f'Median: {currency}{stats["ale_median"]:,.0f}')
        ax1.set_xlabel(f'Annual Loss ({currency})', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Distribution of Annual Losses', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative Distribution (Exceedance Curve)
        ax2 = axes[0, 1]
        sorted_losses = np.sort(annual_losses)
        exceedance_prob = 1 - np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
        ax2.plot(sorted_losses, exceedance_prob * 100, linewidth=2, color='#A23B72')
        ax2.set_xlabel(f'Annual Loss ({currency})', fontsize=11)
        ax2.set_ylabel('Probability of Exceedance (%)', fontsize=11)
        ax2.set_title('Loss Exceedance Curve', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add percentile markers
        for pct in [95, 99]:
            pct_val = stats['percentiles'][f'{pct}th']
            ax2.axvline(pct_val, color='red', linestyle=':', alpha=0.5)
            ax2.text(pct_val, 50, f'{pct}th', rotation=90, va='center', fontsize=9)
        
        # 3. Loss Event Frequency Distribution
        ax3 = axes[1, 0]
        ax3.hist(lef_samples, bins=50, edgecolor='black', alpha=0.7, color='#F18F01')
        ax3.axvline(stats['lef_mean'], color='red', linestyle='--', linewidth=2, label=f'Mean: {stats["lef_mean"]:.3f}')
        ax3.set_xlabel('Loss Event Frequency (events/year)', fontsize=11)
        ax3.set_ylabel('Frequency', fontsize=11)
        ax3.set_title('Distribution of Loss Event Frequency', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Box plot of percentiles
        ax4 = axes[1, 1]
        percentile_data = [stats['percentiles'][p] for p in ['10th', '25th', '50th', '75th', '90th']]
        bp = ax4.boxplot([annual_losses], vert=True, patch_artist=True, 
                         showmeans=True, meanline=True,
                         boxprops=dict(facecolor='#06A77D', alpha=0.7),
                         meanprops=dict(color='red', linewidth=2),
                         medianprops=dict(color='orange', linewidth=2))
        ax4.set_ylabel(f'Annual Loss ({currency})', fontsize=11)
        ax4.set_title('Annual Loss Distribution Summary', fontsize=12, fontweight='bold')
        ax4.set_xticklabels(['ALE'])
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add text annotations
        textstr = f'Mean: {currency}{stats["ale_mean"]:,.0f}\nMedian: {currency}{stats["ale_median"]:,.0f}\n95th: {currency}{stats["percentiles"]["95th"]:,.0f}\n99th: {currency}{stats["percentiles"]["99th"]:,.0f}'
        ax4.text(0.98, 0.97, textstr, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def export_results(self, stats: Dict, scenario_name: str, filename: str):
        """Export results to JSON and CSV"""
        # Export statistics to JSON
        json_data = {
            'scenario_name': scenario_name,
            'n_simulations': self.n_simulations,
            'statistics': stats
        }
        
        json_filename = filename.replace('.csv', '.json')
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"Statistics exported to: {json_filename}")
        
        # Export raw data to CSV
        if self.results is not None:
            df = pd.DataFrame({
                'annual_loss': self.results['annual_losses'],
                'loss_event_frequency': self.results['lef_samples'],
                'threat_event_frequency': self.results['tef_samples'],
                'actual_events': self.results['actual_events']
            })
            df.to_csv(filename, index=False)
            print(f"Raw simulation data exported to: {filename}")


def example_ransomware_scenario():
    """Example: Ransomware attack scenario for SMB"""
    print("\n🔐 EXAMPLE SCENARIO: Ransomware Attack on EU SMB")
    print("="*60)
    
    # Initialize simulation
    sim = FAIRMonteCarloSimulation(n_simulations=10000)
    
    # Threat Event Frequency: Ransomware attempts per year
    # Based on industry data: SMBs face 100-1000 attempts/year
    tef = FAIRDistribution(
        dist_type='pert',
        min_val=100,
        mode_val=300,
        max_val=1000
    )
    
    # Vulnerability: Probability that an attempt succeeds
    # Contact × Action × Vulnerability
    # Assuming: email phishing (high contact) × employee clicks (medium) × unpatched systems (low)
    vulnerability = 0.02  # 2% - most attempts fail
    
    # Primary Loss: Direct costs (ransom, recovery, downtime)
    primary_loss = FAIRDistribution(
        dist_type='lognormal',
        min_val=10000,
        mode_val=50000,
        max_val=200000
    )
    
    # Secondary Loss: Reputation, customer loss, regulatory fines
    secondary_loss = FAIRDistribution(
        dist_type='lognormal',
        min_val=5000,
        mode_val=25000,
        max_val=150000
    )
    
    # Run simulation
    stats = sim.run_simulation(
        tef_dist=tef,
        vuln_prob=vulnerability,
        primary_loss_dist=primary_loss,
        secondary_loss_dist=secondary_loss,
        secondary_loss_prob=0.4  # 40% chance of secondary losses
    )
    
    # Print and visualize results
    sim.print_results(stats, currency="€")
    sim.plot_results(stats, currency="€", save_path="ransomware_risk_analysis.png")
    sim.export_results(stats, "Ransomware Attack", "ransomware_simulation_results.csv")


if __name__ == "__main__":
    # Run example scenario
    example_ransomware_scenario()
    
    print("\n" + "="*60)
    print("To create your own scenario, use the following structure:")
    print("="*60)
    print("""
from fair_monte_carlo import FAIRMonteCarloSimulation, FAIRDistribution

# Create simulation
sim = FAIRMonteCarloSimulation(n_simulations=10000)

# Define your parameters
tef = FAIRDistribution(dist_type='pert', min_val=X, mode_val=Y, max_val=Z)
vulnerability = 0.XX  # Probability 0-1

primary_loss = FAIRDistribution(dist_type='lognormal', min_val=X, mode_val=Y, max_val=Z)
secondary_loss = FAIRDistribution(dist_type='lognormal', min_val=X, mode_val=Y, max_val=Z)

# Run simulation
stats = sim.run_simulation(
    tef_dist=tef,
    vuln_prob=vulnerability,
    primary_loss_dist=primary_loss,
    secondary_loss_dist=secondary_loss,
    secondary_loss_prob=0.X
)

# View results
sim.print_results(stats, currency="€")
sim.plot_results(stats, currency="€")
    """)
